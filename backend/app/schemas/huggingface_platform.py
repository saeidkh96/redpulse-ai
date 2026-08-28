from pydantic import BaseModel, Field
class HFModelInspectRequest(BaseModel): repo_id:str
class HFModelPullRequest(BaseModel): repo_id:str; revision:str|None=None
class HFGenerateRequest(BaseModel): model:str; prompt:str; max_new_tokens:int=Field(default=128,ge=1,le=4096)
