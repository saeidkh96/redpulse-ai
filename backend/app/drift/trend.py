from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class TrendResult:
    slope: float
    normalized_slope: float
    cumulative_change: float
    monotonicity: float
    persistence: float


def calculate_slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    n = len(values)
    mean_x = (n - 1) / 2.0
    mean_y = sum(values) / n

    numerator = 0.0
    denominator = 0.0

    for index, value in enumerate(values):
        x_delta = index - mean_x
        y_delta = value - mean_y

        numerator += x_delta * y_delta
        denominator += x_delta ** 2

    if denominator == 0.0:
        return 0.0

    return numerator / denominator


def calculate_standard_deviation(
    values: list[float],
) -> float:
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    return sqrt(variance)


def calculate_monotonicity(
    values: list[float],
) -> float:
    if len(values) < 2:
        return 0.0

    differences = [
        current - previous
        for previous, current in zip(
            values,
            values[1:],
        )
    ]

    positive = sum(
        difference > 0.0
        for difference in differences
    )

    negative = sum(
        difference < 0.0
        for difference in differences
    )

    total = len(differences)

    if total == 0:
        return 0.0

    return abs(positive - negative) / total


def calculate_persistence(
    values: list[float],
) -> float:
    if len(values) < 3:
        return 0.0

    slope = calculate_slope(values)

    if slope == 0.0:
        return 0.0

    direction = 1.0 if slope > 0.0 else -1.0

    differences = [
        current - previous
        for previous, current in zip(
            values,
            values[1:],
        )
    ]

    aligned = sum(
        1
        for difference in differences
        if difference * direction > 0.0
    )

    return aligned / len(differences)


def analyze_trend(
    values: list[float],
) -> TrendResult:
    if not values:
        raise ValueError("values must not be empty")

    if len(values) == 1:
        return TrendResult(
            slope=0.0,
            normalized_slope=0.0,
            cumulative_change=0.0,
            monotonicity=0.0,
            persistence=0.0,
        )

    slope = calculate_slope(values)

    std = calculate_standard_deviation(values)

    normalized_slope = (
        slope / std
        if std > 0.0
        else 0.0
    )

    cumulative_change = (
        values[-1] - values[0]
    )

    monotonicity = calculate_monotonicity(
        values
    )

    persistence = calculate_persistence(
        values
    )

    return TrendResult(
        slope=slope,
        normalized_slope=normalized_slope,
        cumulative_change=cumulative_change,
        monotonicity=monotonicity,
        persistence=persistence,
    )
