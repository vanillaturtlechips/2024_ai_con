# AI 기반 유해 콘텐츠 필터링 커뮤니티 플랫폼

온라인 커뮤니티에서 발생하는 욕설, 혐오 표현, 폭력적 언어 등 유해 콘텐츠를 AI로 자동 탐지하고 차단하는 게시판 서비스입니다.

---

## 해결한 문제

온라인 커뮤니티에서 관리자 없이도 유해 게시글/댓글이 자동으로 차단되지 않는 문제를 해결합니다.  
실제 한국어 유해 발화 데이터셋(`merged_toxic_data.json`)을 기반으로 욕설, 성차별, 모욕, 외설, 폭력/범죄 조장 표현을 실시간으로 감지합니다.

---

## 주요 기능

### 유해 콘텐츠 자동 탐지
- 게시글 및 댓글 작성 시 내용을 실시간 분석
- **2단계 검사 방식**
  1. 기본 금지어 사전 검사 (즉시 차단)
  2. 데이터셋 기반 고급 패턴 매칭 (유해성 점수 2점 이상 항목만 적용)
- 감지 카테고리: `욕설/비속어`, `성차별`, `모욕`, `외설`, `폭력/범죄`
- 탐지 시 카테고리 명시 후 작성 차단, 로그 기록

### 회원 시스템
- 회원가입 / 로그인 / 로그아웃
- 비밀번호 해시 저장 (Werkzeug)
- 로그인 사용자만 게시글/댓글 작성 가능

### 게시판 CRUD
- 게시글 작성, 조회, 수정, 삭제 (작성자 본인만 수정/삭제 가능)
- 댓글 작성, 삭제
- 페이지네이션 (10개씩)

---

## 기술 스택

| 구분 | 사용 기술 |
|------|-----------|
| Backend | Python, Flask, Flask-Login, Flask-WTF, SQLAlchemy |
| Database | MySQL (Flask-Migrate / Alembic) |
| AI/NLP | 커스텀 규칙 기반 탐지 + 한국어 유해 발화 데이터셋 |
| Frontend | Jinja2 템플릿 |

---

## 프로젝트 구조

```
2024_ai_con/
├── app/
│   ├── __init__.py          # Flask 앱 초기화, DB/Login 설정
│   ├── models.py            # User, Post, Comment 모델
│   ├── routes.py            # 라우팅 및 폼 처리
│   ├── content_detector.py  # 유해 콘텐츠 탐지 엔진
│   └── templates/           # HTML 템플릿
├── migrations/              # DB 마이그레이션
├── logs/                    # 유해 콘텐츠 탐지 로그
├── config.py                # 앱 설정
├── run.py                   # 앱 실행 진입점
└── merged_toxic_data.json   # 한국어 유해 발화 학습 데이터
```

---

## 실행 방법

```bash
# 1. 가상환경 활성화
source venv/Scripts/activate  # Windows
source venv/bin/activate       # Linux/Mac

# 2. DB 마이그레이션
flask db upgrade

# 3. 서버 실행
python run.py
```

> `config.py`에서 DB 연결 정보 및 SECRET_KEY를 환경에 맞게 수정하세요.
