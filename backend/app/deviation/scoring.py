from dataclasses import dataclass


@dataclass(frozen=True)
class SensorDeviationScore:
    mean_zscore: float
    std_ratio: float
    score: float


@dataclass(frozen=True)
class CorrelationDeviationScore:
    baseline: float
    current: float
    delta: float
    score: float


def calculate_mean_zscore(
    baseline_mean: float,
    baseline_std: float,
    current_mean: float,
) -> float:
    if baseline_std <= 0:
        return 0.0

    return abs(
        current_mean - baseline_mean
    ) / baseline_std


def calculate_std_ratio(
    baseline_std: float,
    current_std: float,
) -> float:
    if baseline_std <= 0:
        return 1.0

    ratio = current_std / baseline_std

    if ratio < 1.0:
        ratio = 1.0 / max(ratio, 1e-12)

    return ratio


def normalize_mean_zscore(
    zscore: float,
) -> float:
    return min(zscore / 3.0, 1.0)


def normalize_std_ratio(
    ratio: float,
) -> float:
    if ratio <= 1.0:
        return 0.0

    return min(
        (ratio - 1.0) / 2.0,
        1.0,
    )


def calculate_sensor_deviation(
    *,
    baseline_mean: float,
    baseline_std: float,
    current_mean: float,
    current_std: float,
) -> SensorDeviationScore:
    mean_zscore = calculate_mean_zscore(
        baseline_mean,
        baseline_std,
        current_mean,
    )

    std_ratio = calculate_std_ratio(
        baseline_std,
        current_std,
    )

    mean_score = normalize_mean_zscore(
        mean_zscore
    )

    std_score = normalize_std_ratio(
        std_ratio
    )

    score = (
        mean_score * 0.7
        + std_score * 0.3
    )

    return SensorDeviationScore(
        mean_zscore=mean_zscore,
        std_ratio=std_ratio,
        score=min(score, 1.0),
    )


def calculate_correlation_deviation(
    *,
    baseline: float,
    current: float,
) -> CorrelationDeviationScore:
    delta = abs(
        current - baseline
    )

    score = min(
        delta / 1.0,
        1.0,
    )

    return CorrelationDeviationScore(
        baseline=baseline,
        current=current,
        delta=delta,
        score=score,
    )
