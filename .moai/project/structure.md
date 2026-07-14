# 프로젝트 구조 (structure.md)

> **주의**: 이 프로젝트는 아직 소스 코드가 존재하지 않는 그린필드 상태입니다. 아래 디렉터리 구조는 기존 코드를 스캔하여 도출한 것이 **아니며**, Python 기반 템플릿 문서 생성 도구에 적합한 **권장 시작 구조(제안안)**입니다. 실제 구현 시 팀의 선호나 요구사항에 따라 조정될 수 있습니다.

## 제안 디렉터리 트리

```
markdown_creat/
├── src/
│   └── markdown_creat/          # 메인 패키지 (배포 시 pip 패키지명과 일치 권장)
│       ├── __init__.py
│       ├── cli.py               # CLI 진입점 (argparse/typer/click 등)
│       ├── generator.py         # 템플릿 + 데이터 → .md 생성 핵심 로직
│       ├── loader.py            # 템플릿/데이터 파일 로딩 (yaml/json/toml 등)
│       ├── renderer.py          # 템플릿 렌더링 엔진 래퍼 (예: Jinja2)
│       └── config.py            # 설정 및 기본값 관리
│
├── templates/                   # 사용자 정의/기본 제공 마크다운 템플릿
│   ├── report.md.j2             # 보고서 템플릿 예시
│   ├── meeting_notes.md.j2       # 회의록 템플릿 예시
│   └── README.md                # 템플릿 작성 가이드
│
├── examples/                    # 입력 데이터 및 생성 결과 예시
│   ├── sample_data.yaml
│   └── sample_output.md
│
├── tests/                       # 테스트 코드
│   ├── __init__.py
│   ├── test_generator.py
│   ├── test_loader.py
│   └── test_cli.py
│
├── docs/                        # 프로젝트 문서 (사용법, API 레퍼런스 등, 필요 시)
│
├── .moai/                       # MoAI-ADK 설정 및 SPEC 관리 (이미 존재)
│   ├── project/
│   └── config/
│
├── pyproject.toml               # 패키징/의존성/빌드 설정 (권장: PEP 621 방식)
├── README.md                    # 프로젝트 소개 및 사용법
├── .gitignore
└── CHANGELOG.md
```

## 모듈 구성 개요

- **`src/markdown_creat/cli.py`**: 커맨드라인 진입점. 템플릿 경로와 입력 데이터(파일 또는 인자)를 받아 `generator.py`를 호출.
- **`src/markdown_creat/generator.py`**: 템플릿과 데이터를 조합해 최종 `.md` 문자열/파일을 만드는 핵심 비즈니스 로직. `loader.py`, `renderer.py`에 의존.
- **`src/markdown_creat/loader.py`**: YAML/JSON 등 다양한 포맷의 입력 데이터를 파싱해 파이썬 객체로 변환.
- **`src/markdown_creat/renderer.py`**: 실제 템플릿 엔진(예: Jinja2) 호출을 캡슐화. 추후 템플릿 엔진 교체 시 이 모듈만 수정하면 되도록 설계.
- **`templates/`**: 소스 코드와 분리된 템플릿 자산 디렉터리. 보고서/회의록 등 문서 유형별 기본 템플릿을 보관.
- **`tests/`**: `pytest` 기반 단위/통합 테스트. `src/` 레이아웃과 대응되는 구조 유지.

## 설계 원칙 (제안)

1. **src 레이아웃 사용**: 패키지를 `src/` 하위에 두어 테스트 시 우발적인 로컬 임포트 문제를 방지.
2. **템플릿과 코드의 분리**: 템플릿 파일(`templates/`)은 코드와 독립적으로 관리하여 비개발자도 템플릿을 추가/수정하기 쉽게 함.
3. **CLI와 로직의 분리**: `cli.py`는 얇은 진입점 역할만 하고, 실제 로직은 `generator.py` 등 별도 모듈에 위치시켜 라이브러리로도 재사용 가능하게 함.
4. **테스트 우선 구조**: 초기 단계부터 `tests/` 디렉터리를 마련해 TDD/DDD 워크플로우 적용이 용이하도록 함.

---

*이 구조는 시작점 제안이며, 실제 코드가 작성되기 전 계획 문서입니다. 구현 진행 후 실제 구조와 차이가 발생하면 본 문서를 갱신해야 합니다.*
