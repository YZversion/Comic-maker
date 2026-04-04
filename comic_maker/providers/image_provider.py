"""Image provider. Supports mock, siliconflow, liblib."""

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
    ) -> str:
        if self.provider == "mock":
            return self._mock_generate(prompt, output_path)
        if self.provider == "siliconflow":
            return self._siliconflow_generate(prompt, output_path, seed=seed, negative_prompt=negative_prompt)
        if self.provider == "liblib":
            return self._liblib_generate(prompt, output_path, seed=seed, negative_prompt=negative_prompt)
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
