from __future__ import annotations
class HuggingFaceInferenceAdapter:
    def __init__(self, token:str|None=None, provider:str|None=None) -> None: self.token=token; self.provider=provider
    def text_generation(self, model:str, prompt:str, max_new_tokens:int=128) -> str:
        try: from huggingface_hub import InferenceClient
        except ImportError as exc: raise RuntimeError("Install huggingface_hub") from exc
        client=InferenceClient(token=self.token, provider=self.provider)
        return str(client.text_generation(prompt, model=model, max_new_tokens=max_new_tokens))
