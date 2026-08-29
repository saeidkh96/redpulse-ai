from dataclasses import dataclass
@dataclass(frozen=True)
class ModelVersion: name:str; version:str; metrics:dict[str,float]; stage:str='candidate'
class ModelRegistry:
 def __init__(self): self.models={}; self.champions={}
 def register(self,m): self.models[(m.name,m.version)]=m
 def promote(self,name,version):
  if (name,version) not in self.models: raise KeyError((name,version))
  self.champions[name]=version
class PromotionGate:
 @staticmethod
 def evaluate(champion_metric,challenger_metric,max_drift,observed_drift):
  return {'improved':challenger_metric>champion_metric,'stable':observed_drift<=max_drift,'promote':challenger_metric>champion_metric and observed_drift<=max_drift}
