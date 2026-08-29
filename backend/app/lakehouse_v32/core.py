from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable
import hashlib, json
class LakehouseLayer(str, Enum): BRONZE='bronze'; SILVER='silver'; GOLD='gold'
@dataclass(frozen=True)
class AutoLoaderConfig:
    source_uri:str; format:str='json'; schema_location:str='dbfs:/redpulse/schema/telemetry'; checkpoint_location:str='dbfs:/redpulse/checkpoints/telemetry'; rescued_data_column:str='_rescued_data'
    def cloud_files_options(self): return {'cloudFiles.format':self.format,'cloudFiles.schemaLocation':self.schema_location,'rescuedDataColumn':self.rescued_data_column}
@dataclass(frozen=True)
class DeltaTableSpec:
    catalog:str; schema:str; table:str; layer:LakehouseLayer; partition_by:tuple[str,...]=()
    @property
    def full_name(self): return f'{self.catalog}.{self.schema}.{self.table}'
@dataclass
class LakehouseRecord:
    layer:LakehouseLayer; payload:dict[str,Any]; record_id:str; quality:dict[str,Any]=field(default_factory=dict)
class TelemetryLakehouseTransformer:
    required_fields={'machine_id','ts','metrics'}
    @classmethod
    def bronze(cls,payload):
        rid=hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()[:24]
        return LakehouseRecord(LakehouseLayer.BRONZE,dict(payload),rid,{'raw':True})
    @classmethod
    def silver(cls,record):
        missing=sorted(cls.required_fields-set(record.payload)); metrics=record.payload.get('metrics',{})
        valid_metrics=isinstance(metrics,dict) and all(isinstance(v,(int,float)) for v in metrics.values())
        payload=dict(record.payload)
        if isinstance(metrics,dict): payload['metrics']={str(k):float(v) for k,v in metrics.items() if isinstance(v,(int,float))}
        return LakehouseRecord(LakehouseLayer.SILVER,payload,record.record_id,{'missing_fields':missing,'valid_metrics':valid_metrics,'valid':not missing and valid_metrics})
    @classmethod
    def gold(cls,record):
        if record.layer!=LakehouseLayer.SILVER or not record.quality.get('valid'): raise ValueError('Gold requires a valid Silver record')
        vals=list(record.payload['metrics'].values()); p={'machine_id':record.payload['machine_id'],'ts':record.payload['ts'],'feature_count':len(vals),'metric_mean':sum(vals)/len(vals) if vals else 0.0,'metric_max':max(vals) if vals else 0.0,'metric_min':min(vals) if vals else 0.0,'features':record.payload['metrics']}
        return LakehouseRecord(LakehouseLayer.GOLD,p,record.record_id,{'analytics_ready':True,'source_quality':record.quality})
class MedallionPipeline:
    def process(self,payload):
        b=TelemetryLakehouseTransformer.bronze(payload); s=TelemetryLakehouseTransformer.silver(b); out={'bronze':b,'silver':s}
        if s.quality['valid']: out['gold']=TelemetryLakehouseTransformer.gold(s)
        return out
    def process_many(self,rows:Iterable[dict[str,Any]]): return [self.process(r) for r in rows]
