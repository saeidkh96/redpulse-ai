from dataclasses import dataclass

@dataclass(frozen=True)
class LineageEntry:
    source: str
    dataset_version: str
    feature_version: str
    model_version: str
    prediction_id: str

class LineageRegistry:
    def __init__(self) -> None:
        self.entries: list[LineageEntry] = []

    def record(self, entry: LineageEntry) -> None:
        self.entries.append(entry)
