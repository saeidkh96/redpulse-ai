from dataclasses import asdict, dataclass

from app.features.correlation import pearson_correlation
from app.features.statistics import calculate_statistics


@dataclass(frozen=True)
class FeatureSet:
    sensors: dict[str, dict[str, float | int]]
    correlations: dict[str, float]


class FeatureEngine:
    def build(
        self,
        sensor_series: dict[str, list[float]],
    ) -> FeatureSet:
        if not sensor_series:
            raise ValueError("sensor_series must not be empty")

        sensors: dict[str, dict[str, float | int]] = {}

        for sensor, values in sensor_series.items():
            statistics = calculate_statistics(values)
            sensors[sensor] = asdict(statistics)

        correlations: dict[str, float] = {}

        sensor_names = sorted(sensor_series.keys())

        for index, first_sensor in enumerate(sensor_names):
            for second_sensor in sensor_names[index + 1:]:
                first_values = sensor_series[first_sensor]
                second_values = sensor_series[second_sensor]

                if len(first_values) != len(second_values):
                    continue

                if len(first_values) < 2:
                    continue

                key = f"{first_sensor}__{second_sensor}"

                correlations[key] = pearson_correlation(
                    first_values,
                    second_values,
                )

        return FeatureSet(
            sensors=sensors,
            correlations=correlations,
        )


feature_engine = FeatureEngine()
