from pydantic import BaseModel

class StreamingEventPayload(BaseModel):
    topic: str
    event: dict

class AnalyticsJobRequest(BaseModel):
    name: str
    input_path: str
    output_path: str
    engine: str = "spark"
