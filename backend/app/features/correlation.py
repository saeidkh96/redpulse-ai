import math


def pearson_correlation(
    x: list[float],
    y: list[float],
) -> float:
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    if len(x) < 2:
        raise ValueError("at least two paired values are required")

    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)

    numerator = sum(
        (a - mean_x) * (b - mean_y)
        for a, b in zip(x, y)
    )

    denominator_x = math.sqrt(
        sum(
            (a - mean_x) ** 2
            for a in x
        )
    )

    denominator_y = math.sqrt(
        sum(
            (b - mean_y) ** 2
            for b in y
        )
    )

    denominator = denominator_x * denominator_y

    if denominator == 0:
        return 0.0

    return numerator / denominator
