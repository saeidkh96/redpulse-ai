from dataclasses import dataclass

@dataclass(frozen=True)
class DeploymentCheck:
    name: str
    ok: bool
    detail: str = ""

class DeploymentReadiness:
    def evaluate(self, checks: list[DeploymentCheck]) -> dict:
        failed = [c for c in checks if not c.ok]
        return {
            "ready": not failed,
            "checks": [c.__dict__ for c in checks],
            "failed": [c.name for c in failed],
        }
