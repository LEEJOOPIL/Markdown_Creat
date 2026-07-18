---
id: SPEC-OCR-001
title: "OCR 코어 모듈 — 이미지·PDF 텍스트 추출 (한국어 지원) — 구현 계획"
version: "0.3.0"
status: completed
created: 2026-07-17
updated: 2026-07-18
author: manager-spec
priority: P1
phase: "v0.1.0 target"
module: "src/markdown_creat"
lifecycle: spec-anchored
tags: "ocr, tesseract, pdf, markdown, korean, extraction, shared-module"
tier: M
depends_on: [SPEC-TELEGRAM-001]
---

# SPEC-OCR-001 — 구현 계획 (plan.md)

## §A. 컨텍스트 (Context)

기존 코드의 사진 OCR 로직을 최상위 공유 모듈로 승격·일반화하고, PDF 페이지 OCR 기능을 신규 추가하는 순수 코어 모듈 SPEC. Tier M(신규 모듈 1개 + 완료 SPEC 1개의 공개 함수 재노출 + 다국어 지원 + 다수 오류 경로로 Tier S보다 복잡, Tier L 문턱인 15개 파일·1000 LOC에는 미달).

**의존성 확인**: `depends_on: [SPEC-TELEGRAM-001]`. `status: completed`이며 `extract_image_text(image_path)`(`src/markdown_creat/telegram_bot/ocr.py:18`)가 실제로 구현되어 있다(2026-07-17 확인). `/moai run` 시 Depends_on Pre-flight Check는 이 SPEC이 `status: completed`이므로 통과가 예상된다. 추가 게이트는 없다.

SPEC-PDF-001은 `depends_on`에 포함하지 않는다(0.2.0 경로 (c) 재범위 조정 — §B 참조). 본 SPEC은 `pdf_to_markdown()`을 호출하지도, 수정하지도, 앰언드먼트하지도 않는다. `extract_pdf_text_via_ocr()`는 PyMuPDF를 직접 사용하므로 SPEC-PDF-001의 공개 함수에 의존하지 않는다.

## §B. 핵심 아키텍처 결정 — `pdf_to_markdown()` 통합의 소유권 (경로 a vs b vs c)

manager-spec의 판단: **경로 (c)를 채택** — SPEC-OCR-001은 순수 코어 모듈 SPEC으로 축소하고, `pdf_to_markdown()` 자동 OCR 폴백 통합은 SPEC-PDF-001 자신의 향후 앰언드먼트로 이관한다. 아래에 세 경로를 모두 검토하고 근거를 기록한다.

### 검토한 경로

**경로 (a)**: SPEC-OCR-001이 `depends_on: [SPEC-PDF-001, SPEC-TELEGRAM-001]`을 선언하고, 자신의 본문에서 SPEC-PDF-001의 OCR 배제 조항을 "상위 SPEC으로서" 무효화한다고 서술한다. SPEC-PDF-001 자체는 건드리지 않는다.

**경로 (b)** (0.1.0에서 채택했다가 0.2.0에서 철회): SPEC-OCR-001이 REQ-OCR-009~012로 `pdf_to_markdown()`의 폴백 계약을 서술하면서, 동시에 SPEC-PDF-001이 `completed → in-progress (amendment)` 전환(`amendment_of` 자기 참조, HISTORY `## Amendments`, REQ-PDF-009 문구 갱신)을 별도로 거치도록 M2 마일스톤으로 조율한다.

**경로 (c)** (채택): SPEC-OCR-001은 `src/markdown_creat/ocr.py`와 `telegram_bot/ocr.py` 재노출만 소유한다. REQ-OCR-009~012, `pdf_to_markdown.py` 훅, SPEC-PDF-001 앰언드먼트(M2)를 모두 본 SPEC에서 제거한다. 이 통합은 SPEC-PDF-001 자신의 앰언드먼트가 소유하며, **본 SPEC이 `status: completed`에 도달한 뒤 별도로 작성**된다. `depends_on`은 `[SPEC-TELEGRAM-001]`만 남는다.

### 경로 (b)를 철회한 근거 — 두 가지 결함

**결함 1 — 자기 무효화 전제조건(self-invalidating precondition).** *(0.3.0 D1 정정: 이 결함은 실재하나 0.2.0 서술이 그 위험을 과장했다. 아래는 정정된 서술이다.)* 경로 (b)는 `depends_on: [SPEC-PDF-001, ...]`을 선언하면서 동시에 M2에서 SPEC-PDF-001을 `completed → in-progress`로 전환시킨다.

- **"순환 의존"은 오기다.** 의존 그래프에 사이클은 없다(OCR-001 → PDF-001 단방향). 정확한 명명은 *자기 무효화 전제조건* — SPEC이 자신의 게이트가 검사하는 상태를 스스로 변경하는 패턴이다.
- **preflight 실패 시점 서술 정정.** Depends_on Pre-flight Check는 `spec-workflow.md` § Depends_on Pre-flight Check가 정의하듯 "**Phase 1의 first sub-step, plan-auditor subagent 호출 이전**"에 실행되는 **`/moai run` 진입 시 1회 게이트**다. 그 게이트 시점에 SPEC-PDF-001은 `completed`이므로 **preflight는 통과한다**. M2는 게이트가 이미 통과한 *이후* run-phase 안에서 실행되므로, 이미 통과한 게이트를 소급 실패시키지 않는다. 따라서 0.2.0의 "M2를 수행하는 순간 본 SPEC 자신의 preflight가 실패한다"는 서술은 **사실 오류**였다.
- **실제 위험은 재진입 취약성이다.** PDF-001이 `in-progress`인 상태에서 `/moai run`을 재호출(중단 후 재개, CI 재시도)하면 *그때* preflight가 실패한다. 이는 실재하는 결함이나 "구조적 블로커"가 아니라 "재개 시 override 필요"라는 훨씬 좁은 문제다.
- **`--ignore-deps` 오버라이드는 결함 1을 비결함에 가깝게 만든다.** `spec-workflow.md`는 3-option 블로커(wait / **override** / abort)를 명시하며, override는 `--ignore-deps` + `.moai/logs/depends-on-override.log` 기록으로 **제재된(sanctioned) 정식 경로**다. 즉 결함 1은 최악의 경우에도 "제재된 우회 + 로깅 비용"이지 구조적 블로커가 아니다.
- **0.1.0 acceptance.md §D.1 비판의 정당한 범위(D2).** v0.1.0 §D.1이 "M2 완료 후 통과가 예상된다"고 쓴 것은 게이트가 M2 *이전에* 실행됨을 오해한 혼란스러운 서술이며 — 이 부분의 비판은 타당하다. 다만 그 결함은 "게이트 시점을 오해하고 override를 명시하지 않은 **서술 결함**"에 한정되며, override의 존재 자체를 "암묵적 전제"라 기각할 근거는 아니다(override는 규칙이 문서화한 정식 옵션이다).

경로 (c)는 SPEC-PDF-001을 `depends_on`에서 제거하고 앰언드먼트를 본 SPEC 완료 이후로 미루므로 자기 무효화 패턴 자체가 성립하지 않는다. **단, 경로 (c)의 정당화는 결함 1에 의존하지 않는다 — 아래 결함 2 단독으로 충분하다(D1/D2 결론).**

**결함 2 — 의존 방향 역전 + SSOT 목표 미달성.** 0.1.0 §C의 기술 접근이 명시하듯 `extract_pdf_text_via_ocr()`는 PyMuPDF(`fitz.open` + `page.get_pixmap()`)를, `extract_image_text()`는 pytesseract를 각각 **직접** 사용한다 — 코어 모듈 `ocr.py`는 `pdf_to_markdown()`을 결코 호출하지 않는다. 실제 의존 방향은 그 반대(`pdf_to_markdown.py` → `extract_pdf_text_via_ocr()`)이며, 따라서 SPEC-OCR-001이 SPEC-PDF-001에 의존한다는 0.1.0의 전제 자체가 코드 사실과 어긋났다. 더 결정적으로, 경로 (b)에서는 REQ-OCR-009~012와 개정된 REQ-PDF-009가 **동일한 `pdf_to_markdown()` 계약을 두 문서에 이중 서술**하게 된다. 이는 0.1.0이 경로 (a)를 기각한 바로 그 근거(당시 근거 3 — "두 SPEC을 모두 읽어야 함")를 경로 (b) 스스로 재현하는 것이다. 경로 (b)는 SSOT를 지키려다 SSOT를 깨뜨렸다.

### 경로 (c)의 선택 근거

1. **각 SPEC이 자기 코드의 계약만 서술한다.** `ocr.py`의 계약은 SPEC-OCR-001이, `pdf_to_markdown()`의 계약은 SPEC-PDF-001이 서술한다. 독자가 "이 함수는 텍스트 없는 PDF를 만나면 어떻게 동작하는가?"를 알기 위해 읽어야 할 문서는 SPEC-PDF-001 하나다. 이것이 0.1.0이 의도했던 SSOT 목표를 실제로 달성하는 유일한 배치다.
2. **운영 비용이 절감된다 (D2 — "구조적 결함 제거"가 아님).** 경로 (c)에서는 `--ignore-deps` 오버라이드 승인도, 그 로깅도 필요 없다. 다만 이는 *구조적 결함의 제거*가 아니라 *운영 비용(override 승인 + 로깅) 절감*이다 — override는 `spec-workflow.md`가 문서화한 제재된 3-option 경로이므로(결함 1 참조), 그 회피를 "구조적 이점"으로 계상하는 것은 이중 계산이다. 따라서 이 근거는 경로 (c) 채택의 **부차적** 이점으로만 계상한다. 경로 (c)의 핵심 정당화는 근거 1(SSOT) + 결함 2다.
3. **앰언드먼트 메커니즘 자체는 여전히 유효하며, 올바른 시점에 적용된다.** `spec-frontmatter-schema.md` § Status Enum의 `completed → in-progress (amendment)` 전환은 "해당 SPEC 자신의 공개 함수 동작 계약이 변경되는 경우"를 위한 것이고, `pdf_to_markdown()`의 계약 변경은 정확히 그 경우에 해당한다. 경로 (c)는 이 메커니즘을 **부정하는 것이 아니라 올바른 소유자(SPEC-PDF-001)와 올바른 순서(코어 모듈 완료 후)로 재배치**할 뿐이다. 이 점에서 0.1.0 경로 (b)의 근거 1·2·4는 여전히 타당하며, 다만 그 앰언드먼트를 **SPEC-OCR-001의 run-phase 안에서 조율하려던 것**이 잘못이었다.
4. **의존 순서가 코드 사실과 일치한다.** SPEC-PDF-001의 앰언드먼트는 `extract_pdf_text_via_ocr()`가 실제로 존재한 뒤에야 의미가 있다. 본 SPEC 완료 → SPEC-PDF-001 앰언드먼트 순서는 코드 의존 방향(`pdf_to_markdown.py` → `ocr.py`)을 그대로 따른다.
5. **경로 (a)는 여전히 기각된다.** "상위 SPEC이 하위 완료 SPEC의 배제 조항을 무효화한다"는 거버넌스 패턴은 이 프로젝트에 선례가 없고, 계약 이중 서술 문제(결함 2)도 그대로 안는다.

### 본 SPEC의 범위 경계 (요약)

- **범위 안**: `src/markdown_creat/ocr.py`(신규 코어 모듈, `extract_image_text` + `extract_pdf_text_via_ocr` + `OcrError`), `src/markdown_creat/telegram_bot/ocr.py`(얇은 재노출), `src/markdown_creat/telegram_bot/handlers.py`의 **사진 OCR 호출 지점 1곳**(REQ-OCR-015 — `"kor+eng"` 언어 인자 지정, 최소 변경), `tests/test_telegram_ocr.py` 모킹 경로 갱신 + 사진 경로 언어 인자 테스트, README.
- **범위 밖**: `src/markdown_creat/pdf_to_markdown.py`(**수정하지 않는다**), REQ-PDF-009 문구, SPEC-PDF-001의 frontmatter·HISTORY·§Exclusions, `handlers.py`의 PDF 처리 경로 및 그 외 로직.

**SPEC-TELEGRAM-001은 앰언드먼트 대상이 아니다** — §A/아래 Conflict B에서 서술한 대로 재노출은 공개 계약을 보존하고, `handlers.py` 사진 경로의 언어 인자 추가(REQ-OCR-015)는 언어를 제약하지 않는 REQ-TELEGRAM-007을 *더 충실히 충족*하므로, SPEC-TELEGRAM-001은 `completed` 상태 그대로 유지된다.

### Conflict A — REQ-OCR-013 vs REQ-OCR-015 (검증 결론: 오케스트레이터에 동의 — 문구 충돌, 비실질적)

두 요구사항은 **서로 다른 대상을 제약**하므로 실질적 충돌이 아니라 문구 충돌이다:
- **REQ-OCR-013**은 재노출 모듈 `telegram_bot/ocr.py` **자신의 공개 계약**을 제약한다 — 인라인 로직을 코어 재노출로 옮기는 리팩터가 재노출 경계에서 동작 보존적일 것(언어 인자 없는 `extract_image_text(image_path)` 호출 형태의 시그니처 호환성·반환값·예외 조건 유지). 코어 함수 시그니처 `extract_image_text(image_path: str, lang: str = "eng")`는 lang 없는 호출 형태와 **하위 호환**이므로(기본값 있는 선택적 키워드 인자), 재노출 계약은 보존된다.
- **REQ-OCR-015**는 호출자 `handlers.py`의 **호출 지점 선택**(선택적 lang 인자를 `"kor+eng"`로 지정)을 제약한다. 서로 다른 파일·다른 관심사다.
- **조치**: 0.2.0의 REQ-OCR-013 문구는 "기존 호출자(`handlers.py`)의 ... 관찰 가능한 동작 ... 그대로 유지"로 읽혀 `handlers.py`를 동결하는 것처럼 오독될 여지가 있었다. 0.3.0에서 REQ-OCR-013 문구를 **재노출 모듈 경계로 명확히 한정**하고, 호출자의 언어 인자 지정 여부는 제약하지 않음을 명시했다(spec.md §B). **오케스트레이터의 판단에 동의한다 — 충돌은 문구 수준이며 REQ-OCR-013 재범위로 해소된다.**

### Conflict B — `handlers.py` 소유권 / SPEC-TELEGRAM-001 앰언드먼트 필요 여부 (검증 결론: 오케스트레이터에 동의 — 앰언드먼트 불필요)

`handlers.py`는 SPEC-TELEGRAM-001(`status: completed`) 소유 파일이다. REQ-OCR-015가 이를 수정하려면 SPEC-TELEGRAM-001 앰언드먼트가 필요한가? **아니다.** `.moai/specs/SPEC-TELEGRAM-001/spec.md`를 직접 정독하여 확인한 증거:
- **근거 (1) — REQ-TELEGRAM-007은 OCR 언어를 제약하지 않는다.** spec.md:67 원문: "When 봇이 사진(이미지) 첨부를 수신하면, the bot shall 원본 저장에 더해 **이미지 내 텍스트를 OCR로 추출**하여 해당 메시지의 `.md` 본문에 포함한다(구체 OCR 라이브러리명은 §C 제약 참조)." 언어에 대한 제약이 없으므로, 한국어를 추가로 추출하는 것은 REQ-TELEGRAM-007을 위반이 아니라 *더 충실히 충족*한다.
- **근거 (2) — v0.3.0 HISTORY가 구현 무관 재작성을 기록한다.** spec.md:26(v0.3.0 HISTORY): "REQ-TELEGRAM-006/007의 GEARS shall 절에서 특정 함수·라이브러리 리터럴(`pdf_to_markdown()`, `pytesseract`)을 제거하고 **동작 서술로 재작성**." 즉 REQ-TELEGRAM-007은 의도적으로 구현/언어 무관으로 설계되었다.
- **근거 (3) — 선례.** 본 SPEC은 이미 SPEC-TELEGRAM-001 소유 파일 `telegram_bot/ocr.py`를 REQ-OCR-013/014로 수정하며 앰언드먼트 없이 진행한다(재노출은 공개 계약 보존).
- **동결 조항 부재 확인.** SPEC-TELEGRAM-001의 어떤 sibling REQ(001~018)도 OCR 언어를 제약하거나 `handlers.py`를 동결하지 않는다. §C 제약(spec.md:93)은 `pytesseract` 사용을 명시하나 언어는 제약하지 않는다.
- **결론**: SPEC-TELEGRAM-001 앰언드먼트는 **불필요**하다. **오케스트레이터의 세 근거에 모두 동의한다.** (만약 REQ-TELEGRAM-007이나 sibling이 언어를 제약했다면 앰언드먼트가 필요했을 것이나, 그러한 조항은 존재하지 않는다.)

### REQ-OCR-015의 배선 근거 (D3 — 한국어 종단 인도)

감사 D3는 사용자 승인 결정 #3(한국어)이 아키텍처적으로 좌초되었음을 지적했다: `handlers.py:71`이 `extract_image_text(str(attachment_path))`를 **lang 인자 없이** 호출하고(→ REQ-OCR-006 기본값 `"eng"`), 어떤 REQ/AC도 `lang="kor"`를 어떤 호출자에도 배선하지 않았다(직접 확인: 2026-07-17). 결과적으로 텔레그램 봇에서 한국어 OCR에 도달할 호출 경로가 없었다. REQ-OCR-015는 사진 경로에 한해 이를 배선한다(`handlers.py`의 사진 OCR 호출 → `"kor+eng"`). 이로써 **사진 경로의 한국어는 종단 인도**되어 D3가 사진 경로에 한해 해소된다. **PDF 경로는 여전히 미인도**(SPEC-PDF-001 앰언드먼트 대기) — spec.md §A "인도 범위 명시"에 이 분할을 정확히 기록했다.

### 결번 판단은 git 히스토리가 강화한다 (D9 / Q4)

009~012 결번 유지는 옳다. v0.1.0은 커밋 `8563de2`로 git 히스토리에 **영구 존재**하며 REQ-OCR-001~014를 정의한다(`git show 8563de2:.moai/specs/SPEC-OCR-001/spec.md`). 워킹트리 수정만 미커밋일 뿐 원본은 커밋되어 있으므로 — 재번호 시 v0.3.0의 "REQ-OCR-009"는 히스토리의 동명 식별자(PDF 폴백)와 의미가 충돌한다. 즉 v0.1.0이 git에 영구 보존된다는 사실은 결번 결정을 **약화가 아니라 강화**한다. 결번은 필요한 흉터다.

### D4 — 이연 SPEC-PDF-001 앰언드먼트 앵커: 기계적 앵커 불가 분석 + 이연 레시피

감사 D4는 이연 작업(제거된 REQ-OCR-009~012 semantics)이 산문 앵커만 가지며 유실 위험이 있음을 지적했다. **기계적(frontmatter-level, greppable) 앵커를 지금 생성할 수 있는지** 분석한 결과:

- **제약**: (i) SPEC-PDF-001은 지금 `status: completed` 유지(조기 `in-progress` 전환 자체가 자기 무효화 전제조건 위험), (ii) 새 sibling SPEC 생성 금지(경로 a), (iii) 새 frontmatter 필드·새 status 값 발명 금지, (iv) 순서 제약(앰언드먼트는 SPEC-OCR-001 완료 후) 인코딩.
- **`amendment_of` + `## Amendments` + `completed → in-progress` 3종 세트**(`spec-frontmatter-schema.md` § Status Enum / § Status Transition Ownership Matrix): 이것이 스키마상 정식 앵커이나, **status 전환을 요구**하므로 제약 (i)에 위배 — 지금 생성 불가.
- **`depends_on: [SPEC-OCR-001]`를 SPEC-PDF-001 frontmatter에 지금 추가**: `depends_on`은 스키마상 명확히 지원되는 유일한 순서-인코딩 필드이나, **`completed` SPEC이 `draft` SPEC에 의존한다고 선언**하는 것은 git 사실과 모순된다(PDF-001은 2026-07-16 완료, SPEC-OCR-001 v0.2.0보다 먼저 존재; 완료된 PDF 구현은 OCR에 의존하지 않음). 이는 verification-claim-integrity 원칙에 반하는 **현재-시제 허위 선언**이며, 완료 SPEC이 초안 SPEC을 기다린다는 가독성 스멜을 남긴다.
- **결론**: **현 제약을 모두 존중하면서 지금 생성 가능한, 스키마가 지원하는 기계적 frontmatter 앵커는 존재하지 않는다.** 스키마의 유일한 순서-인코딩 필드(`depends_on`)는 완료 PDF를 허위 선언하고, 스키마의 앰언드먼트 메커니즘(`amendment_of`/`## Amendments`)은 금지된 status 전환을 요구한다.
- **채택한 least-bad 옵션**: (a) spec.md §Exclusions의 지킬 수 없는 단언("최종 서술 위치는 REQ-PDF-009다")을 "예정 위치이나 본 SPEC이 보증하지 않는다"로 하향(적용 완료), (b) 아래 **정확한 이연 앵커 레시피**를 산문이 아닌 실행 가능한 레시피로 선기록하여 다음 독자가 재도출 없이 그대로 적용하도록 한다, (c) **SPEC-PDF-001 파일은 건드리지 않는다**(허위 선언/스멜 회피 — 내 앵커 메커니즘이 PDF 편집을 요구하지 않으므로).
- **이연 앵커 레시피 (SPEC-OCR-001이 `completed`에 도달한 뒤, SPEC-PDF-001 앰언드먼트 작성 시점에 적용)**: SPEC-PDF-001에 대해 — (1) frontmatter `status: completed → in-progress`, (2) `amendment_of: SPEC-PDF-001`(자기 참조 in-place 앰언드먼트) 추가, (3) `depends_on: [SPEC-OCR-001]` 추가(**이 시점에는 참이 되어** Depends_on Pre-flight Check가 앰언드먼트 run을 SPEC-OCR-001 완료에 기계적으로 게이트한다 — 순서 제약이 여기서 비로소 강제된다), (4) HISTORY에 `## Amendments` 하위 섹션 추가(prior_completed_version, prior_completed_sha, rationale, scope=REQ-PDF-009 + §Exclusions OCR 배제), (5) REQ-PDF-009 문구를 자동 OCR 폴백 계약으로 개정하고 §Exclusions의 OCR 배제 조항 수정. 이 레시피가 `depends_on`을 통해 순서를 기계적으로 강제하는 것은 **오직 status가 in-progress로 전환되는 그 시점**이며, 그것이 완료 SPEC을 허위 선언하지 않고 순서를 인코딩하는 유일한 정합적 배치다.

## §C. 기술 접근 (Technical Approach)

- `src/markdown_creat/ocr.py` — 신규 코어 공유 모듈. 두 개의 공개 함수:
  - `extract_image_text(image_path: str, lang: str = "eng") -> str` — 기존 `telegram_bot/ocr.py`의 `extract_image_text()`를 언어 파라미터를 추가하여 일반화. `pytesseract.image_to_string(image_path, lang=lang)` 호출.
  - `extract_pdf_text_via_ocr(pdf_path: str, lang: str = "eng") -> str` — 신규. PyMuPDF로 PDF를 열고 각 페이지를 `page.get_pixmap()`으로 이미지 렌더링 → 임시 파일에 저장 → `extract_image_text()` 재사용으로 OCR → 페이지 순서대로 텍스트 병합. **이 함수는 본 SPEC의 범위 안에 있다** — PyMuPDF를 직접 사용하는 코어 모듈 자신의 함수이며 `pdf_to_markdown()`을 호출하지 않는다. 범위를 벗어나는 것은 이 함수를 호출할 `pdf_to_markdown.py` 쪽의 **훅**뿐이다(§B 경로 c).
  - 예외: `OcrError`(기존 `ImageOcrError`를 일반화한 이름 — 이미지·PDF 페이지 OCR 모두의 실패를 포괄).
- `src/markdown_creat/pdf_to_markdown.py` — **변경 없음**. 자동 OCR 폴백 훅 삽입은 SPEC-PDF-001의 향후 앰언드먼트가 소유하며 본 SPEC 완료 후 별도로 수행된다(§B 경로 c, spec.md §Exclusions).
- `src/markdown_creat/telegram_bot/ocr.py` — 얇은 재노출로 축소:
  ```python
  from markdown_creat.ocr import OcrError as ImageOcrError, extract_image_text
  __all__ = ["extract_image_text", "ImageOcrError"]
  ```
- `src/markdown_creat/telegram_bot/extract.py` — **변경 없음**.
- `src/markdown_creat/telegram_bot/handlers.py` — **사진 OCR 호출 지점 1곳만 최소 변경**(REQ-OCR-015). `handle_photo_message`의 `extract_image_text(str(attachment_path))`(현재 handlers.py:71) → `extract_image_text(str(attachment_path), lang="kor+eng")`로 언어 인자를 추가한다. 임포트 경로(`telegram_bot.ocr`)는 재노출로 인해 변경 불필요하며, 예외 처리(`ImageOcrError` 폴백)·PDF 처리 경로(`handle_document_message`)·그 외 로직은 **변경하지 않는다**. `extract_pdf_text()`는 `pdf_to_markdown()`을 그대로 호출하므로, 향후 SPEC-PDF-001 앰언드먼트가 폴백 훅을 추가하면 그 효과가 이 래퍼를 거쳐 투명하게 적용될 것이다 — 다만 그 동작은 본 SPEC의 범위·인수 기준 밖이다.
- `pyproject.toml` — 변경 없음(기존 `pymupdf`, `pytesseract` 재사용).
- `README.md` — Tesseract `kor` traineddata 시스템 레벨 설치 안내 섹션 추가.

(최종 모듈 분할은 M3~M4에서 확정. 위는 시작 제안.)

## §D. 마일스톤 (결정 번복 가능성 순 — 변경 가능성 높은 결정 우선)

> 사람이 검토할 때 변경 가능성이 가장 높은 결정(공개 API 시그니처 · PDF 페이지 렌더링 방식)을 먼저 배치하고, 기계적 구현/리팩터 단계는 뒤로 미룬다.

### M1 — 코어 OCR 모듈 공개 API 및 예외 계약 확정 (변경 가능성 최상)
- `ocr.py`의 `extract_image_text(image_path, lang="eng")`, `extract_pdf_text_via_ocr(pdf_path, lang="eng")` 시그니처 확정(REQ-OCR-001, 004, 006, 007).
- `OcrError` 예외 하나로 통일할지, 이미지 실패/PDF 렌더링 실패를 별도 하위 클래스로 분리할지 결정 — 최소 범위로 시작(단일 `OcrError`), 필요 시 하위 클래스는 후속 SPEC(REQ-OCR-003, 005).
- 언어팩 미설치 시 오류 문구 계약 확정(REQ-OCR-008) — `pytesseract.TesseractError`의 원본 메시지(언어팩 파일 경로 포함)를 `OcrError`로 감싸 그대로 전달하는 방식으로 별도 파싱 로직 없이 충족 가능함을 확인(구현 시 실제 오류 메시지로 검증).
- 이는 하위 모든 호출자(telegram_bot 재노출, 그리고 향후 SPEC-PDF-001 앰언드먼트가 추가할 `pdf_to_markdown()` 폴백 훅)가 의존하는 계약이므로 사람 검토가 가장 필요한 지점이다. 특히 `extract_pdf_text_via_ocr()`의 시그니처와 반환 계약(페이지 순서 병합 문자열)은 향후 앰언드먼트가 소비할 인터페이스이므로 신중히 확정한다.
- RED: 코어 모듈 성공/실패 경로에 대한 실패 테스트 작성(`pytesseract` 모킹).

### M2 — PDF 페이지 렌더링 방식 및 해상도 결정 (변경 가능성 상)
- `page.get_pixmap()` 호출 시 DPI/줌 매트릭스 결정 — PyMuPDF 기본값(72 DPI)은 OCR 정확도에 부족할 수 있으므로, 더 높은 해상도(예: `dpi=300` 또는 2x 줌 매트릭스)를 기본값으로 채택하고 정확도 대 속도/메모리 트레이드오프를 문서화한다.
- 렌더링된 페이지 이미지를 OCR에 전달하는 방식 확정: 임시 파일 경유(기존 `extract.py`의 write-then-read 패턴과 일관성 유지, 신규 PIL 직접 의존성 회피) vs 인메모리 PIL Image 전달(Pillow를 명시적 의존성으로 추가 필요). **임시 파일 경유 방식을 채택**(§C 결정 — 기존 패턴과의 일관성, 신규 의존성 회피).
- RED: PDF 페이지 → 이미지 → OCR 통합 경로에 대한 실패 테스트 작성(실제 PyMuPDF 픽스처 + `pytesseract` 모킹의 혼합 전략 — §C 참조).

### M3 — `telegram_bot/ocr.py` 재노출 + `handlers.py` 한국어 배선 및 기존 테스트 갱신 확정 (변경 가능성 중)
- 재노출 형태 확정(§C 코드 스니펫). `ImageOcrError` 이름을 하위 호환을 위해 별칭(alias)으로 유지하는 것을 확정(REQ-OCR-013).
- **`handlers.py` 사진 경로 한국어 배선 확정(REQ-OCR-015)**: `handle_photo_message`의 사진 OCR 호출에 언어 인자 `"kor+eng"`를 지정하는 최소 변경을 확정한다. 언어 값은 **리터럴 `"kor+eng"`**(설정 가능화는 §Exclusions로 이연). 이 변경이 SPEC-TELEGRAM-001 앰언드먼트를 요구하지 않는 근거는 §B Conflict B 참조.
- **기존 테스트 파일 갱신**: `tests/test_telegram_ocr.py`의 4개 테스트가 현재 `unittest.mock.patch("markdown_creat.telegram_bot.ocr.pytesseract.image_to_string", ...)` 형태로 모킹한다(직접 확인됨). 재노출 전환 후 실제 `pytesseract` 호출은 `markdown_creat.ocr` 모듈로 이동하므로, 모킹 대상 경로를 `markdown_creat.ocr.pytesseract.image_to_string`로 갱신해야 4개 테스트가 계속 통과한다. 이는 REQ-TELEGRAM-007의 관찰 가능한 동작을 변경하지 않는 기계적 테스트 파일 갱신이다(SPEC-TELEGRAM-001 앰언드먼트 불필요, §B 참조).
- RED: 재노출 계약에 대한 실패 테스트(임포트 경로, 예외 별칭) 작성. 그리고 **사진 경로 언어 인자 테스트(AC-OCR-006a)** 작성 — `handle_photo_message`가 모킹된 `pytesseract.image_to_string`에 `lang="kor+eng"`로 도달하고, 모킹이 반환한 한국어 텍스트가 저장 `.md` 본문에 포함됨을 검증(seam 검증 — 실제 OCR 출력이 아니라 lang 인자·본문 반영을 단언).

### M4 — 구현 (GREEN, 기계적)
- `ocr.py` 최소 구현. `telegram_bot/ocr.py` 재노출로 축소. `handlers.py` 사진 OCR 호출에 `lang="kor+eng"` 인자 추가(REQ-OCR-015, 1줄 최소 변경). `tests/test_telegram_ocr.py` 모킹 경로 갱신 + 사진 경로 언어 인자 테스트. README에 Tesseract `kor` 설치 안내 추가. (`pdf_to_markdown.py`는 건드리지 않는다 — §B 경로 c; `handlers.py`의 PDF 경로·그 외 로직도 건드리지 않는다.)

### M5 — 리팩터 및 품질 게이트 (REFACTOR, 기계적)
- `ruff` + `black` 정리, 커버리지 85% 확인, 중복 제거. `telegram_bot/ocr.py`·`telegram_bot/extract.py` 전체 회귀 테스트(70개 기존 텔레그램 테스트 + 신규 OCR 코어 테스트) 그린 확인. `test_pdf_to_markdown.py`는 `pdf_to_markdown.py`를 변경하지 않으므로 무수정 그린이 기대된다(회귀 확인 목적으로 실행).

## §E. 리스크 (Risks)

- **[테스트 회귀] 기존 70개 텔레그램 테스트**: `telegram_bot/ocr.py` 재노출 전환이 `tests/test_telegram_ocr.py`의 모킹 대상 경로를 깨뜨릴 수 있다(직접 확인됨 — 현재 `markdown_creat.telegram_bot.ocr.pytesseract.image_to_string` 경로 모킹). 완화: M3에서 이 갱신을 명시적 마일스톤으로 지정.
- **[OCR 정확도] Tesseract 기본 설정의 한계**: 이미지 전처리 없이 기본 설정만 사용하므로 저품질 스캔 PDF에서는 OCR 결과가 부정확하거나 비어 있을 수 있다. `extract_pdf_text_via_ocr()`는 인식 텍스트가 없으면 빈 문자열을 반환하므로(REQ-OCR-002 계열의 계약) 조용한 실패는 없으나, "낮은 정확도의 텍스트가 성공으로 처리되는" 경우는 본 SPEC의 범위 밖(§Exclusions — 정확도 튜닝)이다. 빈 결과를 호출자가 어떻게 처리할지(예: `PDFNoTextError` 발생)는 향후 SPEC-PDF-001 앰언드먼트가 정의한다.
- **[외부 바이너리] `kor` traineddata 미설치**: REQ-OCR-008에 따라 명확한 오류로 처리되지만, 사용자가 README를 읽지 않으면 이 오류를 처음 마주할 수 있다. 완화: README에 설치 안내를 명확히 문서화(M4).
- **[해상도/성능] PDF 페이지 렌더링 해상도 트레이드오프**: 높은 DPI는 OCR 정확도를 높이지만 렌더링 시간과 메모리 사용량을 증가시킨다. M2에서 구체적 수치를 확정하고 문서화한다.
- **[라이선스] PyMuPDF AGPL 라이선스 (SPEC-PDF-001에서 이미 리스크로 기록됨)**: 본 SPEC은 PyMuPDF의 기존 의존성을 재사용할 뿐 새로운 라이선스 리스크를 추가하지 않는다. 참고만 함.
- **[인도 공백 / 소비자 미도래] `extract_pdf_text_via_ocr()`의 소비자 부재 (D3)**: 본 SPEC 완료 시점에 `extract_pdf_text_via_ocr()`는 **아직 어떤 호출자도 없는** 신규 코어 함수다 — 그 유일한 예정 소비자는 SPEC-PDF-001 앰언드먼트의 `pdf_to_markdown()` 폴백 훅인데, 그 앰언드먼트는 본 SPEC 완료 후 별도로 작성되며 본 SPEC이 강제할 수 없다(§B D4). 앰언드먼트가 착륙하지 않으면 이 함수는 **미사용 코드(dead code)로 잔존**하고, 동기 사건(스캔 PDF)은 미해결로 남는다. 완화: §B D4의 이연 앵커 레시피 선기록 + §Exclusions 하향으로 유실 위험을 축소했으나, 기계적 강제 앵커는 스키마상 불가하므로(§B D4) 이 리스크는 완전 제거되지 않고 잔존한다. (사진 경로의 한국어는 REQ-OCR-015로 종단 인도되므로 이 리스크는 PDF 경로에 한정된다.)

## §F. 참조

- `spec.md` (요구사항 SSOT), `acceptance.md` (인수 시나리오)
- 재노출 대상 의존 SPEC(앰언드먼트 불필요): `.moai/specs/SPEC-TELEGRAM-001/spec.md`, `plan.md` (`telegram_bot/ocr.py`)
- 후속 작업 소유 SPEC(본 SPEC의 의존 대상 아님): `.moai/specs/SPEC-PDF-001/spec.md`, `plan.md` — `pdf_to_markdown()` 자동 OCR 폴백 통합은 이 SPEC의 향후 앰언드먼트가 소유하며, 본 SPEC이 `status: completed`에 도달한 뒤 별도로 작성된다(§B 경로 c).
- 앰언드먼트 메커니즘 SSOT(향후 SPEC-PDF-001 앰언드먼트 작성 시 참조): `.claude/rules/moai/development/spec-frontmatter-schema.md` § Status Enum, § Status Transition Ownership Matrix
- 의존성 게이트 SSOT: `.claude/rules/moai/workflow/spec-workflow.md` § Depends_on Pre-flight Check (§B 결함 1의 근거)
