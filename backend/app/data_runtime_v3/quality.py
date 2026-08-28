class DataQualityGate:
    def validate(self, record: dict, required: set[str]) -> dict:
        missing = sorted(required - set(record))
        nulls = sorted(k for k, v in record.items() if v is None)
        return {
            "valid": not missing and not nulls,
            "missing": missing,
            "nulls": nulls,
        }
