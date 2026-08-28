from .models import ReadinessCheck
class ProductionValidator:
    def validate(self,components:dict[str,bool])->list[ReadinessCheck]:
        return [ReadinessCheck(name,ok,"available" if ok else "unavailable") for name,ok in sorted(components.items())]
