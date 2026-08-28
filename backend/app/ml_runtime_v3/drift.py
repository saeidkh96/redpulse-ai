from dataclasses import dataclass

@dataclass(frozen=True)
class DriftAssessment:
    model: str
    score: float
    threshold: float

    @property
    def triggered(self) -> bool:
        return self.score >= self.threshold

class RetrainingCoordinator:
    def __init__(self) -> None:
        self.requests: list[dict] = []

    def evaluate(self, assessment: DriftAssessment) -> dict:
        result = {"model": assessment.model, "triggered": assessment.triggered, "score": assessment.score}
        if assessment.triggered:
            self.requests.append(result)
        return result
