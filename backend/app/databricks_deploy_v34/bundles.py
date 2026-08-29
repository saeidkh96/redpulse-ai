from dataclasses import dataclass
@dataclass(frozen=True)
class DeploymentTarget: name:str; workspace_host:str; catalog:str; schema:str
@dataclass(frozen=True)
class DatabricksJobSpec: name:str; entrypoint:str; cluster_key:str='default'; timeout_seconds:int=3600
class AssetBundlePlanner:
    def __init__(self,bundle_name='redpulse'): self.bundle_name=bundle_name
    def render(self,target,jobs):
        return {'bundle':{'name':self.bundle_name},'targets':{target.name:{'workspace':{'host':target.workspace_host},'variables':{'catalog':target.catalog,'schema':target.schema}}},'resources':{'jobs':{j.name:{'name':j.name,'timeout_seconds':j.timeout_seconds,'tasks':[{'task_key':j.name,'spark_python_task':{'python_file':j.entrypoint},'job_cluster_key':j.cluster_key}]} for j in jobs}}}
