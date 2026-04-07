"""Image provider. Supports mock, siliconflow, liblib, comfyui."""

import base64
import os

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config


class ImageProvider:
    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def generate(
        self,
        prompt: str,
        output_path: str,
        seed: int | None = None,
        negative_prompt: str = "",
        ref_image_paths: list[str] | None = None,
    ) -> str:
        if self.provider == "mock":
            return self._mock_generate(prompt, output_path)
        if self.provider == "siliconflow":
            return self._siliconflow_generate(prompt, output_path, seed=seed, negative_prompt=negative_prompt)
        if self.provider == "liblib":
            return self._liblib_generate(prompt, output_path, seed=seed, negative_prompt=negative_prompt)
        if self.provider == "comfyui":
            return self._comfyui_generate(prompt, output_path, seed=seed, ref_image_paths=ref_image_paths or [])
        raise NotImplementedError(f"Provider '{self.provider}' not implemented yet")

    def _mock_generate(self, prompt: str, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        placeholder = output_path + ".txt"
        with open(placeholder, "w", encoding="utf-8") as f:
            f.write(f"[MOCK IMAGE]\n\nPrompt:\n{prompt}\n")
        return placeholder

    def _siliconflow_generate(
        self, prompt: str, output_path: str, seed: int | None = None, negative_prompt: str = ""
    ) -> str:
        import requests

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        body: dict = {
            "model": config.IMAGE_MODEL,
            "prompt": prompt,
            "image_size": "1024x1024",
            "num_inference_steps": 4,
        }
        if seed is not None:
            body["seed"] = seed
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        resp = requests.post(
            "https://api.siliconflow.cn/v1/images/generations",
            headers={
                "Authorization": f"Bearer {config.SILICONFLOW_API_KEY}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        # 支持 url 和 b64_json 两种返回格式
        image_info = data["images"][0]
        if "url" in image_info:
            img_resp = requests.get(image_info["url"], timeout=30)
            img_resp.raise_for_status()
            image_bytes = img_resp.content
        else:
            image_bytes = base64.b64decode(image_info["b64_json"])

        img_path = output_path + ".png"
        with open(img_path, "wb") as f:
            f.write(image_bytes)
        return img_path

    # ------------------------------------------------------------------ liblib
    def _liblib_sign(self, uri: str):
        import hmac
        import time
        import uuid
        from hashlib import sha1

        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        content = "&".join((uri, timestamp, nonce))
        digest = hmac.new(
            config.LIBLIB_SECRET_KEY.encode(),
            content.encode(),
            sha1,
        ).digest()
        signature = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return {
            "AccessKey": config.LIBLIB_ACCESS_KEY,
            "Signature": signature,
            "Timestamp": timestamp,
            "SignatureNonce": nonce,
        }

    def _liblib_generate(
        self, prompt: str, output_path: str, seed: int | None = None, negative_prompt: str = ""
    ) -> str:
        import time
        import requests

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        base_url = "https://openapi.liblibai.cloud"

        # 1. 提交生成任务
        uri = "/api/generate/webui/text2img/ultra"
        params = self._liblib_sign(uri)
        generate_params: dict = {
            "prompt": prompt,
            "aspectRatio": "portrait",
            "imgCount": 1,
            "steps": 30,
        }
        if seed is not None:
            generate_params["seed"] = seed
        if negative_prompt:
            generate_params["negativePrompt"] = negative_prompt
        body = {
            "templateUuid": config.LIBLIB_TEMPLATE_UUID or "5d7e67009b344550bc1aa6ccbfa1d7f4",
            "generateParams": generate_params,
        }
        resp = requests.post(
            base_url + uri,
            params=params,
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"LiblibAI submit error: {data}")
        generate_uuid = data["data"]["generateUuid"]

        # 2. 轮询直到完成
        poll_uri = "/api/generate/status"
        for _ in range(60):
            time.sleep(5)
            poll_params = self._liblib_sign(poll_uri)
            poll_resp = requests.post(
                base_url + poll_uri,
                params=poll_params,
                json={"generateUuid": generate_uuid},
                timeout=15,
            )
            poll_resp.raise_for_status()
            poll_data = poll_resp.json()
            if poll_data.get("code") != 0:
                raise RuntimeError(f"LiblibAI poll error: {poll_data}")
            status = poll_data["data"].get("generateStatus")
            # 5=成功
            if status == 5:
                img_url = poll_data["data"]["images"][0]["imageUrl"]
                img_bytes = requests.get(img_url, timeout=30).content
                img_path = output_path + ".png"
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
                return img_path
            # 3=失败
            if status == 3:
                raise RuntimeError(f"LiblibAI generation failed: {poll_data}")

        raise TimeoutError("LiblibAI generation timed out after 5 minutes")

    # ---------------------------------------------------------------- comfyui
    def _comfyui_upload_image(self, base_url: str, image_path: str) -> str:
        """Upload a local image to ComfyUI's input directory.

        Returns the filename as known by ComfyUI (used in LoadImage nodes).
        """
        import requests

        with open(image_path, "rb") as f:
            resp = requests.post(
                f"{base_url}/upload/image",
                files={"image": (os.path.basename(image_path), f, "image/png")},
                data={"type": "input", "overwrite": "true"},
                timeout=15,
            )
        resp.raise_for_status()
        return resp.json()["name"]

    def _comfyui_generate(
        self, prompt: str, output_path: str, seed: int | None = None,
        ref_image_paths: list[str] | None = None,
    ) -> str:
        import copy
        import json
        import random
        import time
        import uuid
        import requests

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if seed is None:
            seed = random.randint(0, 2**32 - 1)

        # Workflow template matching the user's basictexttopic workflow.
        # Node 13 = positive CLIPTextEncode
        # Node 15 = KSampler (seed injected here)
        # Node 21 = AutoNegativePrompt (seed kept in sync)
        # Node 17 = VAEDecode → we attach a dynamic SaveImage node
        workflow: dict = {
            "12": {
                "inputs": {"ckpt_name": "manga\\hassakuXLIllustrious_v34.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "13": {
                "inputs": {
                    "text": prompt,
                    "clip": ["12", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "14": {
                "inputs": {
                    "text": ["21", 0],
                    "clip": ["12", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "15": {
                "inputs": {
                    "seed": seed,
                    "steps": 25,
                    "cfg": 8,
                    "sampler_name": "dpmpp_sde_gpu",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["12", 0],
                    "positive": ["13", 0],
                    "negative": ["14", 0],
                    "latent_image": ["16", 0],
                },
                "class_type": "KSampler",
            },
            "16": {
                "inputs": {"width": 1216, "height": 1216, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "17": {
                "inputs": {
                    "samples": ["15", 0],
                    "vae": ["12", 2],
                },
                "class_type": "VAEDecode",
            },
            "21": {
                "inputs": {
                    "postive_prompt": "",
                    "base_negative": "text, watermark",
                    "enhancenegative": 1,
                    "insanitylevel": 1,
                    "base_model": "SDXL",
                    "seed": seed,
                },
                "class_type": "AutoNegativePrompt",
            },
            # Dynamically added SaveImage so we can retrieve via /view API
            "99": {
                "inputs": {
                    "filename_prefix": "comic_panel",
                    "images": ["17", 0],
                },
                "class_type": "SaveImage",
            },
        }

        base_url = config.COMFYUI_URL.rstrip("/")
        client_id = str(uuid.uuid4())

        # Inject IPAdapter nodes when ref images are available
        valid_refs = [p for p in (ref_image_paths or []) if p and os.path.isfile(p)]
        if valid_refs:
            ref_filename = self._comfyui_upload_image(base_url, valid_refs[0])
            workflow["100"] = {
                "inputs": {"ipadapter_file": config.IPADAPTER_MODEL},
                "class_type": "IPAdapterModelLoader",
            }
            workflow["101"] = {
                "inputs": {"clip_name": config.IPADAPTER_CLIP_VISION},
                "class_type": "CLIPVisionLoader",
            }
            workflow["102"] = {
                "inputs": {"image": ref_filename, "upload": "image"},
                "class_type": "LoadImage",
            }
            workflow["103"] = {
                "inputs": {
                    "model": ["12", 0],
                    "ipadapter": ["100", 0],
                    "image": ["102", 0],
                    "clip_vision": ["101", 0],
                    "weight": config.IPADAPTER_WEIGHT,
                    "weight_type": "linear",
                    "combine_embeds": "concat",
                    "start_at": 0.0,
                    "end_at": 1.0,
                    "embeds_scaling": "V only",
                },
                "class_type": "IPAdapterAdvanced",
            }
            # Route KSampler through the IPAdapter-conditioned model
            workflow["15"]["inputs"]["model"] = ["103", 0]

        # 1. Submit prompt
        resp = requests.post(
            f"{base_url}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=15,
        )
        resp.raise_for_status()
        prompt_id = resp.json()["prompt_id"]

        # 2. Poll /history until finished (max 10 min)
        for _ in range(120):
            time.sleep(5)
            hist_resp = requests.get(f"{base_url}/history/{prompt_id}", timeout=10)
            hist_resp.raise_for_status()
            history = hist_resp.json()
            if prompt_id not in history:
                continue
            outputs = history[prompt_id].get("outputs", {})
            # Node 99 is our SaveImage node
            if "99" not in outputs:
                continue
            images = outputs["99"].get("images", [])
            if not images:
                raise RuntimeError("ComfyUI returned no images in node 99 output")
            img_info = images[0]
            # 3. Download via /view
            dl_resp = requests.get(
                f"{base_url}/view",
                params={
                    "filename": img_info["filename"],
                    "subfolder": img_info.get("subfolder", ""),
                    "type": img_info.get("type", "output"),
                },
                timeout=60,
            )
            dl_resp.raise_for_status()
            img_path = output_path + ".png"
            with open(img_path, "wb") as f:
                f.write(dl_resp.content)
            return img_path

        raise TimeoutError("ComfyUI generation timed out after 10 minutes")
