from dataclasses import dataclass
@dataclass(frozen=True)
class UncertainPrediction:
    value:float; lower:float; upper:float; confidence:float
class UncertaintyEstimator:
    def interval(self,value,uncertainty,confidence=0.9):
        u=max(0.0,float(uncertainty)); v=float(value)
        return UncertainPrediction(round(v,6),round(max(0,v-u),6),round(min(1,v+u),6),round(max(0,min(1,confidence)),6))
class MultimodalFusionEngine:
    def fuse(self,modalities):
        num=den=0.0; evidence=[]
        for name,(score,confidence) in modalities.items():
            s=max(0,min(1,float(score))); c=max(0,min(1,float(confidence))); num+=s*c; den+=c; evidence.append({'modality':name,'score':s,'confidence':c})
        return {'fused_score':round(num/den if den else 0.0,6),'evidence':evidence}
@dataclass(frozen=True)
class InterventionEstimate:
    action:str; expected_risk_delta:float; expected_health_delta:float; confidence:float
class CausalMaintenanceEstimator:
    def estimate(self,action,current_risk,historical_effect,support):
        sf=min(1.0,max(0,support)/20.0); e=max(-1,min(1,float(historical_effect))); r=max(0,min(1,float(current_risk)))
        return InterventionEstimate(action,round(-abs(e)*r,6),round(abs(e)*(1-r),6),round(0.4+0.5*sf,6))
class ProbabilisticRUL:
    def estimate(self,health_score,drift_score,max_hours=1000.0):
        h=max(0,min(1,float(health_score))); d=max(0,min(1,float(drift_score))); mean=float(max_hours)*h*(1-0.55*d); spread=max(10.0,mean*(0.08+0.25*d))
        return {'mean_hours':round(max(0,mean),2),'p10_hours':round(max(0,mean-1.28*spread),2),'p90_hours':round(max(0,mean+1.28*spread),2)}
@dataclass(frozen=True)
class TimeSeriesModelSpec:
    provider:str; model_id:str; task:str; enabled:bool=False
class TimeSeriesFoundationModelGateway:
    def __init__(self): self.specs={}
    def register(self,name,spec): self.specs[name]=spec
    def get(self,name): return self.specs[name]
