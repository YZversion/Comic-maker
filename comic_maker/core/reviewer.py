def review_prompt(prompt: str) -> str:
    print("\n--- Prompt 草稿 ---")
    print(prompt)
    edited = input("\n直接回车接受，或输入修改后的 prompt：\n").strip()
    return edited if edited else prompt


def approve_or_retry(panel_id: str) -> tuple[bool, str]:
    """返回 (是否通过, 不通过的原因)"""
    ans = input(f"\n[{panel_id}] 是否通过？(y/n): ").strip().lower()
    if ans == "y":
        return True, ""
    reason = input("请输入重试原因（如：人物动作不对/构图需改）：\n").strip()
    return False, reason
