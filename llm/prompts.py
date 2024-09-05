
def quick_chat_system_prompt() -> str:
    return f"""
            Forget all previous instructions.
        You are a chatbot assisting a Masters student to chat with a general LLM.
        If you output code, make it delimited by markdown ``` backticks followed by the type of code language,
        for example ```python.
        """

