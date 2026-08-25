import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorStatistics:
    count: int
    mean: float
    std: float
    minimum: float
    maximum: float
    median: float
    slope: float


def calculate_statistics(
    values: list[float],
) -> SensorStatistics:
    if not values:
        raise ValueError("values must not be empty")

    count = len(values)
    mean = sum(values) / count

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / count

    std = math.sqrt(variance)

    ordered = sorted(values)
    middle = count // 2

    if count % 2 == 0:
        median = (
            ordered[middle - 1]
            + ordered[middle]
        ) / 2
    else:
        median = ordered[middle]

    minimum = min(values)
    maximum = max(values)

    if count == 1:
        slope = 0.0
    else:
        x_mean = (count - 1) / 2

        numerator = sum(
            (index - x_mean) * (value - mean)
            for index, value in enumerate(values)
        )

        denominator = sum(
            (index - x_mean) ** 2
            for index in range(count)
        )

        slope = numerator / denominator

    return SensorStatistics(
        count=count,
        mean=mean,
        std=std,
        minimum=minimum,
        maximum=maximum,
        median=median,
        slope=slope,
    )
