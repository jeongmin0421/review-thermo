"""리뷰 온도 규칙 3개. 규칙은 SPEC.md 2장을 보세요. (세션 2에서 AI와 함께 구현)"""

POSITIVE = "positive"
NEGATIVE = "negative"

POSITIVE_THRESHOLD = 0.5  # 이 점수 이상이면 긍정
TEMPERATURE_SCALE = 100  # 점수(0~1)를 온도(0~100)로 바꾸는 배수
TEMPERATURE_DIGITS = 1  # 온도는 소수점 첫째 자리까지
HIGH_RATING_MIN = 4  # 별점 4~5는 높은 별점
LOW_RATING_MAX = 2  # 별점 1~2는 낮은 별점


def to_label(score: float) -> str:
    """score를 "positive" / "negative" 로 바꾼다. 규칙: SPEC.md 2장."""
    return POSITIVE if score >= POSITIVE_THRESHOLD else NEGATIVE


def to_temperature(score: float) -> float:
    """score를 리뷰 온도(0~100)로 바꾼다. 규칙: SPEC.md 2장."""
    return round(score * TEMPERATURE_SCALE, TEMPERATURE_DIGITS)


def is_mismatch(rating: int, label: str) -> bool:
    """별점과 내용이 반대인지 알려 준다. 규칙: SPEC.md 2장."""
    if rating >= HIGH_RATING_MIN:
        expected = POSITIVE
    elif rating <= LOW_RATING_MAX:
        expected = NEGATIVE
    else:
        return False  # 별점 3은 기대하는 라벨이 없으므로 항상 불일치가 아님
    return label != expected

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
