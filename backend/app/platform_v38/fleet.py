from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class MachineVector:
    machine_id:str; features:tuple[float,...]

class FleetSimilarity:
    @staticmethod
    def cosine(a:MachineVector,b:MachineVector)->float:
        if len(a.features)!=len(b.features): raise ValueError("feature dimensions differ")
        dot=sum(x*y for x,y in zip(a.features,b.features)); na=sqrt(sum(x*x for x in a.features)); nb=sqrt(sum(y*y for y in b.features))
        return 0.0 if not na or not nb else dot/(na*nb)
    def rank(self,target:MachineVector,candidates:list[MachineVector])->list[tuple[str,float]]:
        return sorted(((c.machine_id,self.cosine(target,c)) for c in candidates),key=lambda x:x[1],reverse=True)
