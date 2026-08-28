from fastapi import APIRouter
from app.schemas.huggingface_platform import HFGenerateRequest,HFModelInspectRequest,HFModelPullRequest
from app.services.huggingface_platform import huggingface_platform_service
router=APIRouter(prefix="/huggingface",tags=["huggingface"])
@router.post("/models/inspect")
def inspect_model(body:HFModelInspectRequest): return huggingface_platform_service.inspect(body.repo_id)
@router.post("/models/pull")
def pull_model(body:HFModelPullRequest): return huggingface_platform_service.pull(body.repo_id,body.revision)
@router.post("/generate")
def generate(body:HFGenerateRequest): return huggingface_platform_service.generate(body.model,body.prompt,body.max_new_tokens)
