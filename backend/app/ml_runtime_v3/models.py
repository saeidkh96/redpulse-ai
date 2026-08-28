class FailureRiskModel:
    def predict(self, features: dict[str, float]) -> dict:
        health = float(features.get("health_score", 1.0))
        deviation = float(features.get("deviation_score", 0.0))
        drift = float(features.get("drift_score", 0.0))
        risk = max(0.0, min(1.0, (1-health)*0.5 + deviation*0.3 + drift*0.2))
        return {"failure_risk": round(risk, 6)}

class RemainingUsefulLifeModel:
    def __init__(self, max_hours: float = 1000.0) -> None:
        self.max_hours = max_hours

    def predict(self, features: dict[str, float]) -> dict:
        health = max(0.0, min(1.0, float(features.get("health_score", 1.0))))
        drift = max(0.0, min(1.0, float(features.get("drift_score", 0.0))))
        remaining = self.max_hours * health * (1.0 - 0.5 * drift)
        return {"remaining_useful_life_hours": round(max(0.0, remaining), 2)}
