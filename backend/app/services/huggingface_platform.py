from __future__ import annotations
from app.integrations.huggingface.platform import HuggingFaceModelPlatform
class HuggingFacePlatformService:
    def __init__(self, platform:HuggingFaceModelPlatform|None=None)->None: self.platform=platform or HuggingFaceModelPlatform()
    def inspect(self,repo_id:str): return self.platform.inspect(repo_id)
    def pull(self,repo_id:str,revision:str|None=None)->dict: return {"path":str(self.platform.cache.pull(repo_id,revision))}
    def generate(self,model:str,prompt:str,max_new_tokens:int=128)->dict: return {"text":self.platform.generate(model,prompt,max_new_tokens)}
huggingface_platform_service=HuggingFacePlatformService()
