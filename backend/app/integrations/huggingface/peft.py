from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class LoraConfigSpec:
    r:int=8; alpha:int=16; dropout:float=0.05; target_modules:tuple[str,...]=()
class PeftTrainingAdapter:
    def build_lora_config(self, spec:LoraConfigSpec):
        try: from peft import LoraConfig
        except ImportError as exc: raise RuntimeError("Install peft") from exc
        kwargs={"r":spec.r,"lora_alpha":spec.alpha,"lora_dropout":spec.dropout}
        if spec.target_modules: kwargs["target_modules"]=list(spec.target_modules)
        return LoraConfig(**kwargs)
