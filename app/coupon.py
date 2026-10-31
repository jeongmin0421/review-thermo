"""쿠폰 규칙. 규칙은 SPEC_COUPON.md 4장(R1~R5)을 보세요. (세션 4에서 AI와 함께 구현)"""

import secrets
import string
import threading

from app.thermo import NEGATIVE

APOLOGY = "APOLOGY"
THANKS = "THANKS"

APOLOGY_AMOUNT = 5000  # R1. 사과 쿠폰 금액(원)
THANKS_AMOUNT = 1000  # R2. 감사 쿠폰 금액(원)
THANKS_MIN_LENGTH = 30  # R2. 감사 쿠폰을 받는 최소 글자 수 (앞뒤 공백 제외)
CODE_LENGTH = 8  # R5. 코드 뒤쪽 무작위 글자 수
CODE_CHARS = string.ascii_uppercase + string.digits  # R5. 대문자·숫자

# R4. 쿠폰을 발급한 review_id만 메모리에 기억한다 (리뷰 글은 저장하지 않음)
_issued_ids: set[str] = set()
_lock = threading.Lock()


def choose_coupon(label: str, text: str) -> tuple[str, int] | None:
    """R1~R3. 줄 쿠폰의 (종류, 금액)을 정한다. 대상이 아니면 None."""
    if label == NEGATIVE:
        return APOLOGY, APOLOGY_AMOUNT
    if len(text.strip()) >= THANKS_MIN_LENGTH:
        return THANKS, THANKS_AMOUNT
    return None


def make_code(coupon_type: str) -> str:
    """R5. <coupon_type>-<대문자·숫자 8자리 무작위> 코드를 만든다."""
    suffix = "".join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))
    return f"{coupon_type}-{suffix}"


def is_issued(review_id: str) -> bool:
    """R4. 이미 쿠폰을 발급한 review_id인가."""
    with _lock:
        return review_id in _issued_ids


def claim(review_id: str) -> bool:
    """R4. review_id를 발급 기록에 남긴다. 이미 있으면 False (동시에 두 요청이 와도 하나만 성공)."""
    with _lock:
        if review_id in _issued_ids:
            return False
        _issued_ids.add(review_id)
        return True

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
