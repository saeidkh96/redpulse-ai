from dataclasses import asdict, dataclass

from app.drift.trend import (
    TrendResult,
    analyze_trend,
)


@dataclass(frozen=True)
class DriftSignal:
    trend: dict
    score: float
    state: str


@dataclass(frozen=True)
class DriftReport:
    overall_score: float
    state: str
    signals: dict[str, dict]


class DriftDetector:
    def analyze_signal(
        self,
        values: list[float],
    ) -> DriftSignal:
        trend = analyze_trend(values)

        slope_component = min(
            abs(trend.normalized_slope) / 0.50,
            1.0,
        )

        persistence_component = min(
            trend.persistence,
            1.0,
        )

        monotonicity_component = min(
            trend.monotonicity,
            1.0,
        )

        score = (
            slope_component * 0.50
            + persistence_component * 0.30
            + monotonicity_component * 0.20
        )

        score = min(
            max(score, 0.0),
            1.0,
        )

        state = self._state(score)

        return DriftSignal(
            trend=asdict(trend),
            score=score,
            state=state,
        )

    def analyze(
        self,
        signal_history: dict[str, list[float]],
    ) -> DriftReport:
        if not signal_history:
            raise ValueError(
                "signal_history must not be empty"
            )

        signals: dict[str, dict] = {}
        scores: list[float] = []

        for signal, values in signal_history.items():
            if len(values) < 3:
                continue

            result = self.analyze_signal(
                values
            )

            signals[signal] = {
                "trend": result.trend,
                "score": result.score,
                "state": result.state,
            }

            scores.append(result.score)

        if not scores:
            raise ValueError(
                "at least one signal with three values is required"
            )

        overall_score = (
            sum(scores) / len(scores)
        )

        overall_score = min(
            max(overall_score, 0.0),
            1.0,
        )

        overall_state = self._state(
            overall_score
        )

        return DriftReport(
            overall_score=overall_score,
            state=overall_state,
            signals=signals,
        )

    @staticmethod
    def _state(
        score: float,
    ) -> str:
        if score < 0.30:
            return "stable"

        if score < 0.60:
            return "emerging"

        return "drifting"


drift_detector = DriftDetector()
