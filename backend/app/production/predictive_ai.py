from dataclasses import dataclass
from typing import Protocol, Any

class Predictor(Protocol):
    def predict(self, features: dict[str,float]) -> dict[str,Any]: ...
@dataclass(frozen=True,slots=True)
class ModelRef: name:str; version:str; stage:str="candidate"
class ModelServingRouter:
    def __init__(self): self._models={}; self._champions={}
    def register(self,ref:ModelRef,predictor:Predictor): self._models[(ref.name,ref.version)]=predictor
    def promote(self,ref:ModelRef):
        if (ref.name,ref.version) not in self._models: raise KeyError("model not registered")
        self._champions[ref.name]=ref.version
    def predict(self,name:str,features:dict[str,float]): return self._models[(name,self._champions[name])].predict(features)

@dataclass(frozen=True,slots=True)
class DriftSignal: model:str; score:float; threshold:float
class RetrainingPolicy:
    def should_retrain(self,signal:DriftSignal)->bool: return signal.score >= signal.threshold

class ChampionChallenger:
    @staticmethod
    def choose(champion_metric:float,challenger_metric:float,higher_is_better:bool=True)->str:
        better=challenger_metric>champion_metric if higher_is_better else challenger_metric<champion_metric
        return "challenger" if better else "champion"

@dataclass(frozen=True,slots=True)
class FeatureContract:
    version:str; required:frozenset[str]
    def validate(self,features:dict)->None:
        missing=self.required-set(features)
        if missing: raise ValueError(f"missing features: {sorted(missing)}")

def prediction_envelope(model:ModelRef,prediction:dict,evidence:dict)->dict:
    return {"model":{"name":model.name,"version":model.version},"prediction":prediction,"evidence":evidence}

class FailureRiskModel:
    def predict(self,features:dict[str,float])->dict:
        vals=[max(0.0,min(1.0,float(v))) for v in features.values()]
        risk=sum(vals)/len(vals) if vals else 0.0
        return {"failure_risk":round(risk,6)}
class RemainingUsefulLifeModel:
    def __init__(self,max_hours:float=1000.0): self.max_hours=max_hours
    def predict(self,features:dict[str,float])->dict:
        degradation=max([float(v) for v in features.values()] or [0.0]); return {"rul_hours":max(0.0,self.max_hours*(1.0-min(1.0,degradation)))}
