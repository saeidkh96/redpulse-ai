from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
@dataclass(frozen=True)
class ModelRequest:
    model:str; prompt:str; max_new_tokens:int=128
class TextGenerationProvider(Protocol):
    def text_generation(self, model:str, prompt:str, max_new_tokens:int=128)->str: ...
class ModelGateway:
    def __init__(self)->None: self._providers:dict[str,TextGenerationProvider]={}
    def register(self,name:str,provider:TextGenerationProvider)->None: self._providers[name]=provider
    def generate(self,provider:str,request:ModelRequest)->str:
        if provider not in self._providers: raise LookupError(f"Unknown model provider: {provider}")
        return self._providers[provider].text_generation(request.model,request.prompt,request.max_new_tokens)
