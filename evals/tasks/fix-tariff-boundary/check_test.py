import pytest

from app.tariff import price_chf


@pytest.mark.parametrize(
    "weight, expected",
    [(0.5, 7.00), (2.0, 7.00), (2.01, 9.70), (10.0, 9.70), (10.01, 20.50), (30.0, 20.50)],
)
def test_tier_boundaries_are_inclusive(weight, expected):
    assert price_chf(weight) == pytest.approx(expected)


def test_over_30_kg_is_rejected():
    with pytest.raises(ValueError):
        price_chf(30.01)
