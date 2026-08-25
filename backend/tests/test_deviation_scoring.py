import pytest

from app.deviation.scoring import (
    calculate_correlation_deviation,
    calculate_mean_zscore,
    calculate_sensor_deviation,
    calculate_std_ratio,
)


def test_mean_zscore() -> None:
    result = calculate_mean_zscore(
        baseline_mean=10.0,
        baseline_std=2.0,
        current_mean=14.0,
    )

    assert result == pytest.approx(2.0)


def test_mean_zscore_zero_std() -> None:
    result = calculate_mean_zscore(
        baseline_mean=10.0,
        baseline_std=0.0,
        current_mean=20.0,
    )

    assert result == 0.0


def test_std_ratio_increase() -> None:
    result = calculate_std_ratio(
        baseline_std=2.0,
        current_std=4.0,
    )

    assert result == pytest.approx(2.0)


def test_std_ratio_decrease() -> None:
    result = calculate_std_ratio(
        baseline_std=4.0,
        current_std=2.0,
    )

    assert result == pytest.approx(2.0)


def test_sensor_deviation_low() -> None:
    result = calculate_sensor_deviation(
        baseline_mean=10.0,
        baseline_std=2.0,
        current_mean=10.5,
        current_std=2.1,
    )

    assert result.mean_zscore < 1.0
    assert result.score < 0.3


def test_sensor_deviation_high() -> None:
    result = calculate_sensor_deviation(
        baseline_mean=10.0,
        baseline_std=2.0,
        current_mean=18.0,
        current_std=5.0,
    )

    assert result.mean_zscore >= 3.0
    assert result.score > 0.7


def test_correlation_deviation() -> None:
    result = calculate_correlation_deviation(
        baseline=0.85,
        current=0.35,
    )

    assert result.delta == pytest.approx(0.5)
    assert result.score == pytest.approx(0.5)
