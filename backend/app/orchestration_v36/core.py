from dataclasses import dataclass,field
@dataclass(frozen=True)
class PipelineTask: task_id:str; depends_on:tuple[str,...]=(); retries:int=1
@dataclass
class DagSpec:
 dag_id:str; schedule:str; tasks:list[PipelineTask]=field(default_factory=list)
 def validate(self):
  ids={t.task_id for t in self.tasks}
  if len(ids)!=len(self.tasks): raise ValueError("Duplicate task_id")
  for t in self.tasks:
   missing=set(t.depends_on)-ids
   if missing: raise ValueError(f"Missing dependencies: {sorted(missing)}")
class RetrainingOrchestrator:
 def plan(self,model_name,drift_score,threshold):
  flag=drift_score>=threshold; return {'model':model_name,'should_retrain':flag,'pipeline':['snapshot_data','train','evaluate','register'] if flag else []}
