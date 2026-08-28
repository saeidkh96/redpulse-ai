from dataclasses import dataclass
@dataclass(frozen=True)
class ModelVersion:
    name:str; version:str; metric:float; stage:str='candidate'
class ModelRegistryV31:
    def __init__(self): self.models={}; self.champions={}
    def register(self,m): self.models[(m.name,m.version)]=m; return m
    def promote(self,name,version): self.champions[name]=version; return self.models[(name,version)]
    def champion(self,name):
        v=self.champions.get(name); return self.models.get((name,v)) if v else None
class ExperimentTrackerV31:
    def __init__(self): self.runs=[]
    def log(self,model,metrics,params=None):
        r={'model':model,'metrics':dict(metrics),'params':dict(params or {})}; self.runs.append(r); return r
