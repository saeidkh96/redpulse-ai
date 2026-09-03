from dataclasses import dataclass
from enum import Enum

class ModelStage(str,Enum): CANDIDATE="candidate"; CHAMPION="champion"; ARCHIVED="archived"
@dataclass
class ModelRecord:
    name:str; version:str; metric:float; stage:ModelStage=ModelStage.CANDIDATE
class ModelLifecycle:
    def __init__(self): self.records:dict[tuple[str,str],ModelRecord]={}
    def register(self,r:ModelRecord): self.records[(r.name,r.version)]=r; return r
    def promote(self,name:str,version:str)->ModelRecord:
        target=self.records[(name,version)]
        for r in self.records.values():
            if r.name==name and r.stage is ModelStage.CHAMPION: r.stage=ModelStage.ARCHIVED
        target.stage=ModelStage.CHAMPION; return target
    def champion(self,name:str): return next((r for r in self.records.values() if r.name==name and r.stage is ModelStage.CHAMPION),None)
