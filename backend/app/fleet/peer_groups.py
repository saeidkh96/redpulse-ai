from __future__ import annotations

from dataclasses import dataclass

from app.fleet.similarity import (
    MachineBehaviorProfile,
    MachineSimilarity,
    machine_similarity_engine,
)


@dataclass(frozen=True)
class PeerGroup:
    target_machine_id: str
    peers: list[MachineSimilarity]
    minimum_similarity: float

    @property
    def size(self) -> int:
        return len(self.peers)


class PeerGroupEngine:
    def build(
        self,
        target: MachineBehaviorProfile,
        candidates: list[MachineBehaviorProfile],
        *,
        minimum_similarity: float = 0.55,
        limit: int = 25,
    ) -> PeerGroup:
        peers = machine_similarity_engine.rank(
            target,
            candidates,
            minimum_similarity=minimum_similarity,
            limit=limit,
        )
        return PeerGroup(
            target_machine_id=target.machine_id,
            peers=peers,
            minimum_similarity=minimum_similarity,
        )


peer_group_engine = PeerGroupEngine()
