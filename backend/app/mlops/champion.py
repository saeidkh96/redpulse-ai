from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelEvaluation:
    version: str
    precision: float
    recall: float
    false_alert_rate: float
    lead_time_score: float
    maintenance_outcome_score: float


@dataclass(frozen=True)
class ChampionDecision:
    winner_version: str
    challenger_won: bool
    champion_score: float
    challenger_score: float
    reason: str


class ChampionChallengerEngine:
    def compare(
        self,
        champion: ModelEvaluation,
        challenger: ModelEvaluation,
    ) -> ChampionDecision:
        champion_score = self._score(champion)
        challenger_score = self._score(challenger)
        challenger_won = challenger_score > champion_score

        return ChampionDecision(
            winner_version=challenger.version if challenger_won else champion.version,
            challenger_won=challenger_won,
            champion_score=round(champion_score, 4),
            challenger_score=round(challenger_score, 4),
            reason=(
                "challenger_outperformed_champion"
                if challenger_won
                else "champion_retained"
            ),
        )

    @staticmethod
    def _score(item: ModelEvaluation) -> float:
        return (
            item.precision * 0.24
            + item.recall * 0.24
            + (1.0 - item.false_alert_rate) * 0.18
            + item.lead_time_score * 0.16
            + item.maintenance_outcome_score * 0.18
        )
