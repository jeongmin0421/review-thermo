"""2차 쿠폰 API 테스트. 예시표는 SPEC_COUPON.md 4장(R1~R7)을 그대로 옮겼습니다.

발급 기록이 테스트끼리 섞이지 않도록, 테스트마다 새 review_id를 만들어 씁니다.
"""

import re
import uuid

import pytest

URL = "/v1/coupons/issue"
NOT_ISSUED = {"issued": False, "coupon_type": None, "amount": None, "code": None}


def new_id() -> str:
    """다른 테스트와 겹치지 않는 review_id."""
    return f"t-{uuid.uuid4().hex[:12]}"


def text_of(length: int) -> str:
    """글자 수가 정확히 length인 리뷰 글."""
    return "가" * length


def issue(client, review_id: str, text: str):
    return client.post(URL, json={"review_id": review_id, "text": text})


def assert_issued(r, coupon_type: str, amount: int):
    assert r.status_code == 200
    j = r.json()
    assert j["issued"] is True
    assert j["coupon_type"] == coupon_type
    assert j["amount"] == amount


def assert_not_issued(r):
    assert r.status_code == 200
    assert r.json() == NOT_ISSUED


# ---------- R1. 사과 쿠폰 ----------
@pytest.mark.parametrize(
    ("score", "length", "expected"),
    [
        pytest.param(0.1, 10, "APOLOGY", id="0.1_10"),
        pytest.param(0.4999, 10, "APOLOGY", id="0.4999_10_boundary_below"),
        pytest.param(0.5, 10, None, id="0.5_10_boundary"),
        pytest.param(0.4999, 30, "APOLOGY", id="0.4999_30_apology_first"),
    ],
)
def test_r1_apology(make_client, score, length, expected):
    """label이 negative이면 글자 수와 상관없이 APOLOGY 5,000원."""
    r = issue(make_client(score), new_id(), text_of(length))
    if expected:
        assert_issued(r, expected, 5000)
    else:
        assert_not_issued(r)


# ---------- R2. 감사 쿠폰 ----------
@pytest.mark.parametrize(
    ("score", "text", "expected"),
    [
        pytest.param(0.9, text_of(45), "THANKS", id="0.9_45"),
        pytest.param(0.5, text_of(30), "THANKS", id="0.5_30_boundary"),
        pytest.param(0.9, text_of(29), None, id="0.9_29_boundary_below"),
        pytest.param(0.9, " " + text_of(30) + "  ", "THANKS", id="0.9_30_with_spaces"),
    ],
)
def test_r2_thanks(make_client, score, text, expected):
    """label이 positive이고 30자 이상이면 THANKS 1,000원."""
    r = issue(make_client(score), new_id(), text)
    if expected:
        assert_issued(r, expected, 1000)
    else:
        assert_not_issued(r)


# ---------- R3. 대상 아님 ----------
@pytest.mark.parametrize(
    ("score", "text", "issued"),
    [
        pytest.param(0.9, "좋아요", False, id="0.9_3"),
        pytest.param(0.5, text_of(29), False, id="0.5_29_boundary"),
        pytest.param(0.9, text_of(30), True, id="0.9_30_boundary"),
    ],
)
def test_r3_not_eligible(make_client, score, text, issued):
    """positive이고 30자 미만이면 200 + issued=false, 나머지 null."""
    r = issue(make_client(score), new_id(), text)
    if issued:
        assert_issued(r, "THANKS", 1000)
    else:
        assert_not_issued(r)


# ---------- R4. 중복 발급 금지 ----------
def test_r4_same_review_id_twice(make_client):
    """발급한 review_id로 같은 글을 다시 요청하면 409."""
    client, rid = make_client(0.1), new_id()
    assert_issued(issue(client, rid, "배송 최악"), "APOLOGY", 5000)
    assert issue(client, rid, "배송 최악").status_code == 409


def test_r4_same_review_id_other_text(make_client):
    """글이 달라도 review_id가 같으면 409."""
    client, rid = make_client(0.1), new_id()
    assert_issued(issue(client, rid, "배송 최악"), "APOLOGY", 5000)
    assert issue(client, rid, "포장도 엉망").status_code == 409


def test_r4_other_review_id(make_client):
    """다른 review_id는 앞선 발급과 상관없이 발급된다."""
    client = make_client(0.1)
    assert_issued(issue(client, new_id(), "배송 최악"), "APOLOGY", 5000)
    assert_issued(issue(client, new_id(), "배송 최악"), "APOLOGY", 5000)


def test_r4_not_issued_is_not_recorded(make_client):
    """미발급(issued=false)은 기록하지 않으므로 다시 요청해도 200 + issued=false."""
    client, rid = make_client(0.9), new_id()
    assert_not_issued(issue(client, rid, "좋아요"))
    assert_not_issued(issue(client, rid, "좋아요"))


# ---------- R5. 쿠폰 코드 ----------
@pytest.mark.parametrize(
    ("score", "text", "coupon_type"),
    [
        pytest.param(0.1, "배송 최악", "APOLOGY", id="APOLOGY"),
        pytest.param(0.9, text_of(30), "THANKS", id="THANKS"),
    ],
)
def test_r5_code_format(make_client, score, text, coupon_type):
    """code는 <coupon_type>-<대문자·숫자 8자리>."""
    r = issue(make_client(score), new_id(), text)
    assert r.status_code == 200
    assert re.fullmatch(rf"{coupon_type}-[A-Z0-9]{{8}}", r.json()["code"])


def test_r5_codes_differ(make_client):
    """서로 다른 review_id 2건의 code는 서로 다르다."""
    client = make_client(0.1)
    code1 = issue(client, new_id(), "배송 최악").json()["code"]
    code2 = issue(client, new_id(), "배송 최악").json()["code"]
    assert code1 != code2


# ---------- R6. 입력 거절 ----------
@pytest.mark.parametrize(
    ("body", "status"),
    [
        pytest.param({"review_id": "", "text": "배송 최악"}, 422, id="review_id_empty"),
        pytest.param({"review_id": "   ", "text": "배송 최악"}, 422, id="review_id_blank"),
        pytest.param({"review_id": "x" * 51, "text": "배송 최악"}, 422, id="review_id_51"),
        pytest.param({"review_id": "R6", "text": ""}, 422, id="text_empty"),
        pytest.param({"review_id": "R6", "text": "   "}, 422, id="text_blank"),
        pytest.param({"review_id": "R6", "text": text_of(501)}, 422, id="text_501"),
        pytest.param({"text": "배송 최악"}, 422, id="review_id_missing"),
    ],
)
def test_r6_rejected(make_client, body, status):
    """입력이 허용 범위를 벗어나면 422."""
    assert make_client(0.1).post(URL, json=body).status_code == status


def test_r6_review_id_50_ok(make_client):
    """review_id 50자는 허용(경계)."""
    rid = (uuid.uuid4().hex + "x" * 50)[:50]
    assert_issued(issue(make_client(0.1), rid, "배송 최악"), "APOLOGY", 5000)


def test_r6_text_500_ok(make_client):
    """text 500자는 허용(경계)."""
    assert_issued(issue(make_client(0.1), new_id(), text_of(500)), "APOLOGY", 5000)


def test_r6_rejected_is_not_recorded(make_client):
    """422로 거절된 review_id는 기록되지 않아, 올바르게 다시 보내면 발급된다."""
    client, rid = make_client(0.1), new_id()
    assert issue(client, rid, "").status_code == 422
    assert_issued(issue(client, rid, "배송 최악"), "APOLOGY", 5000)


# ---------- R7. AI 부품 고장 ----------
def test_r7_ai_down_then_recovered(broken_client, make_client):
    """AI가 고장 나면 503, 기록이 남지 않으므로 복구 후 같은 review_id로 발급된다."""
    rid = new_id()
    assert issue(broken_client, rid, "배송 최악").status_code == 503
    assert_issued(issue(make_client(0.1), rid, "배송 최악"), "APOLOGY", 5000)

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
