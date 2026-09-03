from dataclasses import dataclass

@dataclass(frozen=True)
class Principal:
    subject:str; tenant_id:str; roles:frozenset[str]
class Authorization:
    @staticmethod
    def require(principal:Principal,tenant_id:str,role:str)->None:
        if principal.tenant_id!=tenant_id: raise PermissionError("cross-tenant access rejected")
        if role not in principal.roles: raise PermissionError("required role missing")
