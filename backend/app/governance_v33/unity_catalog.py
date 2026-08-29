from dataclasses import dataclass
from enum import Enum
class DataClassification(str,Enum): PUBLIC='public'; INTERNAL='internal'; CONFIDENTIAL='confidential'; RESTRICTED='restricted'
@dataclass(frozen=True)
class CatalogGrant: principal:str; securable:str; privileges:tuple[str,...]
@dataclass(frozen=True)
class LineageEdge: source:str; target:str; transformation:str
class UnityCatalogGovernance:
    def __init__(self): self.grants=[]; self.lineage=[]; self.classifications={}
    def grant(self,principal,securable,privileges):
        g=CatalogGrant(principal,securable,tuple(sorted(set(privileges)))); self.grants.append(g); return g
    def classify(self,obj,classification): self.classifications[obj]=classification
    def add_lineage(self,source,target,transformation):
        e=LineageEdge(source,target,transformation); self.lineage.append(e); return e
    def can(self,principal,securable,privilege): return any(g.principal==principal and g.securable==securable and privilege.upper() in {p.upper() for p in g.privileges} for g in self.grants)
