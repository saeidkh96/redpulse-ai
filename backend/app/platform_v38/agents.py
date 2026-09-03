from dataclasses import dataclass

@dataclass(frozen=True)
class MaintenanceProposal:
    machine_id:str; summary:str; evidence:tuple[str,...]; requires_human_approval:bool=True
class MaintenanceAgent:
    def propose(self,machine_id:str,evidence:list[str],risk:float)->MaintenanceProposal:
        if not evidence: raise ValueError("grounded evidence is required")
        level="high" if risk>=.75 else "elevated" if risk>=.5 else "monitor"
        return MaintenanceProposal(machine_id,f"{level} failure risk; review maintenance evidence",tuple(evidence),True)
    def authorize_physical_action(self,*_args,**_kwargs): raise PermissionError("physical maintenance requires external human-approved execution")
