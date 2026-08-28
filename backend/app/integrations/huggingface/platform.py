from __future__ import annotations
from .hub import HuggingFaceHubAdapter
from .metadata import ModelCardSync
from .cache import ModelCache
from .inference import HuggingFaceInferenceAdapter
from .gateway import ModelGateway, ModelRequest
class HuggingFaceModelPlatform:
    def __init__(self, token:str|None=None)->None:
        self.hub=HuggingFaceHubAdapter(token); self.metadata=ModelCardSync(); self.cache=ModelCache(hub=self.hub); self.inference=HuggingFaceInferenceAdapter(token); self.gateway=ModelGateway(); self.gateway.register("huggingface",self.inference)
    def inspect(self,repo_id:str): return self.metadata.normalize(self.hub.model_info(repo_id))
    def generate(self,model:str,prompt:str,max_new_tokens:int=128)->str: return self.gateway.generate("huggingface",ModelRequest(model,prompt,max_new_tokens))
