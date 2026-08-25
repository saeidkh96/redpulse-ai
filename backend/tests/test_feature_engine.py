import pytest

from app.features.correlation import pearson_correlation
from app.features.engine import feature_engine
from app.features.statistics import calculate_statistics


def test_statistics() -> None:
    result = calculate_statistics(
        [1.0, 2.0, 3.0, 4.0, 5.0]
    )

    assert result.count == 5
    assert result.mean == pytest.approx(3.0)
    assert result.minimum == 1.0
    assert result.maximum == 5.0
    assert result.median == 3.0
    assert result.slope == pytest.approx(1.0)


def test_positive_correlation() -> None:
    result = pearson_correlation(
        [1.0, 2.0, 3.0, 4.0],
        [2.0, 4.0, 6.0, 8.0],
    )

    assert result == pytest.approx(1.0)


def test_feature_engine() -> None:
    result = feature_engine.build(
        {
            "load": [50.0, 60.0, 70.0, 80.0],
            "current": [6.0, 7.0, 8.0, 9.0],
            "temperature": [55.0, 60.0, 65.0, 70.0],
        }
    )

    assert result.sensors["load"]["count"] == 4
    assert result.sensors["load"]["mean"] == pytest.approx(65.0)

    assert result.correlations[
        "current__load"
    ] == pytest.approx(1.0)

    assert result.correlations[
        "load__temperature"
    ] == pytest.approx(1.0)


def test_empty_feature_input() -> None:
    with pytest.raises(
        ValueError,
        match="sensor_series must not be empty",
    ):
        feature_engine.build({})
