from dataclasses import dataclass
from math import exp

@dataclass(frozen=True)
class FailureEstimate:
    risk:float; horizon_hours:float|None; confidence:float; evidence:tuple[str,...]
class FailureEstimator:
    def estimate(self,deviation:float,drift:float,trajectory_match:float,uncertainty:float=0.1)->FailureEstimate:
        z=1.7*deviation+1.3*drift+1.8*trajectory_match-2.0
        risk=1/(1+exp(-z)); confidence=max(0.0,min(1.0,1-uncertainty)); horizon=None if risk<0.5 else max(1.0,168*(1-risk))
        evidence=tuple(n for n,v in (("behavioral_deviation",deviation),("slow_drift",drift),("historical_trajectory_match",trajectory_match)) if v>=0.6)
        return FailureEstimate(risk,horizon,confidence,evidence)
