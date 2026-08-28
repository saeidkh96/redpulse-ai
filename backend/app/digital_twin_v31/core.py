from __future__ import annotations
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import time
@dataclass(slots=True)
class TwinState:
    machine_id:str
    timestamp:float=field(default_factory=time.time)
    telemetry:dict[str,float]=field(default_factory=dict)
    health_score:float=1.0
    deviation_score:float=0.0
    drift_score:float=0.0
@dataclass(frozen=True)
class Scenario:
    name:str; overrides:dict[str,float]; horizon_hours:float=24.0
@dataclass(frozen=True)
class ScenarioResult:
    name:str; projected_health:float; projected_risk:float; projected_drift:float
class MachineDigitalTwin:
    def __init__(self,initial:TwinState): self.state=initial; self.history=[deepcopy(initial)]
    def update(self,telemetry:dict[str,float],**scores):
        self.state.telemetry.update(telemetry)
        for k in ('health_score','deviation_score','drift_score'):
            if k in scores and scores[k] is not None: setattr(self.state,k,max(0.0,min(1.0,float(scores[k]))))
        self.history.append(deepcopy(self.state)); return self.state
    def simulate(self,scenario:Scenario):
        load=float(scenario.overrides.get('load',self.state.telemetry.get('load',0.5)))
        vib=float(scenario.overrides.get('vibration',self.state.telemetry.get('vibration',0.2)))
        stress=max(0.0,min(1.0,0.55*load+0.45*vib)); h=min(1.0,scenario.horizon_hours/168.0)
        ph=max(0.0,self.state.health_score-stress*0.35*h); pd=min(1.0,self.state.drift_score+stress*0.30*h)
        pr=max(0.0,min(1.0,(1-ph)*0.65+pd*0.35))
        return ScenarioResult(scenario.name,round(ph,6),round(pr,6),round(pd,6))
class FleetDigitalTwin:
    def __init__(self): self.twins={}
    def register(self,twin): self.twins[twin.state.machine_id]=twin
    def simulate(self,scenario):
        results={k:v.simulate(scenario) for k,v in self.twins.items()}; ranked=sorted(results,key=lambda k:results[k].projected_risk,reverse=True)
        return {'scenario':scenario.name,'machines':{k:asdict(v) for k,v in results.items()},'risk_ranking':ranked}
