import pytest

from app.drift.trend import (
    analyze_trend,
    calculate_monotonicity,
    calculate_persistence,
    calculate_slope,
)


def test_positive_linear_slope() -> None:
    values = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
    ]

    assert calculate_slope(values) == pytest.approx(
        1.0
    )


def test_negative_linear_slope() -> None:
    values = [
        5.0,
        4.0,
        3.0,
        2.0,
        1.0,
    ]

    assert calculate_slope(values) == pytest.approx(
        -1.0
    )


def test_flat_series_has_zero_slope() -> None:
    values = [
        5.0,
        5.0,
        5.0,
        5.0,
    ]

    assert calculate_slope(values) == pytest.approx(
        0.0
    )


def test_monotonicity_for_increasing_series() -> None:
    values = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
    ]

    assert calculate_monotonicity(
        values
    ) == pytest.approx(1.0)


def test_noisy_series_has_lower_monotonicity() -> None:
    values = [
        1.0,
        3.0,
        2.0,
        4.0,
        3.0,
    ]

    assert calculate_monotonicity(values) < 1.0


def test_persistence_for_consistent_trend() -> None:
    values = [
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
    ]

    assert calculate_persistence(
        values
    ) == pytest.approx(1.0)


def test_analyze_trend() -> None:
    result = analyze_trend(
        [
            10.0,
            10.5,
            11.0,
            11.5,
            12.0,
        ]
    )

    assert result.slope > 0.0
    assert result.normalized_slope > 0.0
    assert result.cumulative_change == pytest.approx(
        2.0
    )
    assert result.monotonicity == pytest.approx(
        1.0
    )
    assert result.persistence == pytest.approx(
        1.0
    )


def test_single_value_series() -> None:
    result = analyze_trend([10.0])

    assert result.slope == 0.0
    assert result.normalized_slope == 0.0
    assert result.cumulative_change == 0.0
    assert result.monotonicity == 0.0
    assert result.persistence == 0.0


def test_empty_series_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="values must not be empty",
    ):
        analyze_trend([])
