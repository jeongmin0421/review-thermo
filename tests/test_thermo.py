"""리뷰 온도 규칙 3개의 테스트. 예시표는 SPEC.md 3장을 그대로 옮겼습니다."""

import pytest

from app.thermo import is_mismatch, to_label, to_temperature


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        pytest.param(0.9, "positive", id="0.9"),
        pytest.param(0.5, "positive", id="0.5_boundary"),
        pytest.param(0.4999, "negative", id="0.4999"),
        pytest.param(0.1, "negative", id="0.1"),
    ],
)
def test_to_label(score, expected):
    """score가 0.5 이상이면 positive, 아니면 negative."""
    assert to_label(score) == expected


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        pytest.param(0.8732, 87.3, id="0.8732"),
        pytest.param(0.5, 50.0, id="0.5"),
        pytest.param(0.0, 0.0, id="0.0"),
        pytest.param(1.0, 100.0, id="1.0"),
    ],
)
def test_to_temperature(score, expected):
    """score × 100 을 소수점 첫째 자리까지 반올림."""
    assert to_temperature(score) == expected


@pytest.mark.parametrize(
    ("rating", "label", "expected"),
    [
        pytest.param(5, "negative", True, id="5_negative"),
        pytest.param(4, "negative", True, id="4_negative"),
        pytest.param(2, "positive", True, id="2_positive"),
        pytest.param(1, "positive", True, id="1_positive"),
        pytest.param(3, "negative", False, id="3_negative"),
        pytest.param(5, "positive", False, id="5_positive"),
        pytest.param(1, "negative", False, id="1_negative"),
    ],
)
def test_is_mismatch(rating, label, expected):
    """별점 4~5인데 negative, 별점 1~2인데 positive이면 True. 별점 3은 항상 False."""
    assert is_mismatch(rating, label) == expected

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
