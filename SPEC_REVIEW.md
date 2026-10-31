# 명세서 — 리뷰 온도계 (내가 AI와 함께 쓴 버전)

> `SPEC_TEMPLATE.md`를 바탕으로 AI와 대화하며 정한 내용입니다.

## 1. 이 기능은 무엇을 하나요? (한 문장)

- 리뷰 한 건과 별점을 받아 긍정/부정, 리뷰 온도(0~100℃), 별점 불일치 여부를 돌려준다.

## 2. 입력 (무엇을 받나요?)

| 이름 | 종류(글자/숫자) | 허용 범위 | 예 |
|---|---|---|---|
| text | 글자 | 앞뒤 공백을 지운 뒤 1~500자 | "배송도 빠르고 품질도 좋아요" |
| rating | 숫자(정수) | 1~5 | 5 |

## 3. 출력 (무엇을 돌려주나요?)

| 이름 | 종류 | 뜻 | 예 |
|---|---|---|---|
| label | 글자 | 긍정이면 "positive", 부정이면 "negative" | "positive" |
| score | 숫자(0~1) | AI가 준 '긍정일 확률' (소수 넷째 자리까지) | 0.8732 |
| temperature | 숫자(0~100) | 리뷰 온도. 뜨거울수록 좋은 리뷰 | 87.3 |
| mismatch | 참/거짓 | 별점과 내용이 반대인가 | false |

## 4. 규칙 (어떻게 정하나요?)

- 긍정/부정 기준: score가 0.5 이상이면 "positive", 아니면 "negative" (0.5는 긍정)
- 리뷰 온도 계산법: score × 100 을 소수점 첫째 자리까지 반올림
- 별점과 내용이 '반대'라는 기준: 별점 4~5인데 "negative", 또는 별점 1~2인데 "positive"이면 true. 별점 3은 항상 false

## 5. 예시표 (이 표가 그대로 테스트가 됩니다)

| 입력 | 기대하는 출력 |
|---|---|
| to_label(0.9) | "positive" |
| to_label(0.5) | "positive" (경계값) |
| to_label(0.4999) | "negative" |
| to_label(0.1) | "negative" |
| to_temperature(0.8732) | 87.3 |
| to_temperature(0.5) | 50.0 |
| to_temperature(0.0) | 0.0 |
| to_temperature(1.0) | 100.0 |
| is_mismatch(5, "negative") | True |
| is_mismatch(4, "negative") | True |
| is_mismatch(2, "positive") | True |
| is_mismatch(1, "positive") | True |
| is_mismatch(3, "negative") | False |
| is_mismatch(5, "positive") | False |
| is_mismatch(1, "negative") | False |

## 6. 이런 입력은 거절합니다

- 빈 글, 공백만 있는 글, 500자를 넘는 글 → 422
- 별점이 0이나 6처럼 1~5를 벗어나거나 정수가 아님 → 422
- AI 부품이 응답하지 못함 → 503

## 7. AI와 대화하면서 새로 알게 된 것, 애매했던 것

- 경계값(score 0.5, 별점 3)은 어느 쪽인지 따로 정해 두어야 했다.
- 중립(neutral)을 둘지 고민했지만, 화면과 응답 모양에 neutral이 없어서 두지 않았다.
- score가 0~1을 벗어나면 어떻게 할지는 아직 정하지 않았다. 지금은 AI 부품이 항상 0~1을 준다고 본다.
- 공식 `SPEC.md`가 루트가 아니라 `추후이동/` 폴더에 있어서, 문서들이 가리키는 위치와 달랐다.
