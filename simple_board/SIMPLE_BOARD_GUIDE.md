# simple_board 구조와 로그인 보안 정리

> 게시판 + 회원 + 댓글 + JWT 인증 · 2026-10-06 기준
> VS Code에서 **Cmd + Shift + V**를 누르면 미리보기로 볼 수 있습니다.

이 문서는 두 부분으로 나뉩니다.

1. **파일별 역할**: 폴더가 왜 이렇게 나뉘어 있고, 요청 하나가 어떤 파일을 거쳐 가는지
2. **보안 개념**: 비밀번호 해싱, JWT, Bearer 인증, 권한 확인

---

## 1부. 파일별 역할

### 1-1. 한눈에 보는 폴더 구조

```text
simple_board/
├── main.py                  앱 시작점: 라우터 등록, CORS, 전역 예외 처리
├── .env                     비밀값 (DB 계정, SECRET_KEY) ※ git에 올라가지 않음
│
├── core/                    앱 전체에서 쓰는 설정·공통 기능
│   ├── config.py            .env 값을 읽어 settings 객체로 제공
│   ├── lifespan.py          서버 시작/종료 시 할 일 (테이블 생성)
│   ├── security.py          비밀번호 해싱/검증 (pwdlib, Argon2)
│   └── dependencies.py      Depends로 주입할 함수 → get_current_user
│
├── utils/
│   └── security.py          JWT 토큰 만들기/검증하기 (pyjwt)
│
├── repository/              DB와 직접 연결되는 계층
│   ├── database.py          엔진, 세션(get_db), Base, init_db
│   └── models/              DB 테이블 = 파이썬 클래스 (SQLAlchemy)
│       ├── user.py          board_users 테이블
│       ├── board.py         boards 테이블
│       └── comments.py      comments 테이블
│
├── schemas/                 요청/응답 데이터 모양 검사 (Pydantic)
│   ├── user.py              UserCreate, UserLogin, Token, 비밀번호 규칙 …
│   ├── board.py             BoardCreate, BoardUpdate, BoardResponse, 페이지 응답
│   └── comment.py           CommentCreate, CommentUpdate
│
├── services/                실제 업무 로직 (CRUD, 권한 확인)
│   ├── user.py              회원가입, 로그인(토큰 발급), 정보 수정
│   ├── board.py             게시글 CRUD, 페이지네이션, 작성자 확인
│   └── comment.py           댓글 CRUD
│
├── routers/                 URL과 함수 연결, 예외 → HTTP 응답 변환
│   ├── user_router.py       /auth …
│   ├── board_router.py      /boards …
│   └── comment_router.py    /comments …
│
└── exceptions/              우리가 정의한 예외(에러) 이름
    ├── user.py              UserNotFound, InvalidPassword, UserCredentials …
    └── board.py             BoardNotFound, CommentNotFound, BoardPermission
```

### 1-2. 계층(레이어)별 역할

같은 일을 한 파일에 몰아넣지 않고 **역할마다 나눈 것**이 핵심입니다.

| 계층 | 하는 일 | 하지 않는 일 | 비유 |
| :--- | :--- | :--- | :--- |
| **routers** | URL 받기, `Depends`로 재료 받기, 예외를 `HTTPException`으로 바꾸기 | DB 쿼리, 업무 규칙 | 식당 카운터 직원 |
| **schemas** | 들어오고 나가는 데이터 검사 (타입, 길이, 비밀번호 규칙) | DB 저장 | 주문서 양식 |
| **services** | 진짜 일: 조회·저장·수정·삭제, "본인 글인가?" 판단 | HTTP 상태코드 결정 | 주방 요리사 |
| **repository** | DB 연결, 테이블 정의 | 업무 판단 | 창고 |
| **exceptions** | "무슨 문제가 났는지" 이름 붙이기 | 응답 만들기 | 문제 유형 쪽지 |
| **core / utils** | 설정, 암호화, 토큰, 인증 의존성 | — | 공용 도구함 |

**왜 services는 `HTTPException`을 쓰지 않을까?**
services는 "게시글이 없다(`BoardNotFoundException`)"는 사실만 알립니다. 그걸 404로 보낼지 정하는 건 router의 몫입니다. 그래서 services 코드는 FastAPI가 없어도 이해할 수 있는 순수한 파이썬 코드로 남습니다.

### 1-3. `schemas` vs `models` (가장 헷갈리는 부분)

| | `repository/models/` | `schemas/` |
| :--- | :--- | :--- |
| 라이브러리 | SQLAlchemy | Pydantic |
| 대상 | **DB 테이블** | **API로 주고받는 JSON** |
| 예시 | `User` (password 컬럼에 해시 저장) | `UserCreate` (password에 평문 + 규칙 검사) |
| 응답에 password? | 들어 있음 | `UserResponse`에는 **없음** |

DB 모델을 그대로 응답하면 비밀번호 해시까지 나갈 수 있습니다. 그래서 응답용 schema를 따로 만들고 `response_model`로 지정해 필요한 필드만 내보냅니다.

### 1-4. 테이블 관계

```text
board_users (User)
   │ 1
   ├──────< boards (Board)          board.user_id → board_users.user_id
   │ 1          │ 1
   └──────< comments (Comment) >────┘  comment.user_id, comment.board_id
```

- `relationship`은 컬럼이 아니라 파이썬 객체끼리 연결하는 설정입니다. `board.user.name`, `board.comments`처럼 접근할 수 있습니다.
- `select_one`의 `selectinload`는 게시글을 가져올 때 작성자와 댓글(+ 댓글 작성자)까지 **미리 한꺼번에** 가져오는 설정입니다.

### 1-5. 요청 하나의 흐름

**예: 로그인한 사용자가 게시글 수정 `PUT /boards/3`**

```text
React ── PUT /boards/3
         Header: Authorization: Bearer eyJhbGci...
         Body:   {"title": "새 제목"}
  │
  ▼
main.py              /boards prefix → board_router로 전달
  │
  ▼
board_router.put_board
  ├─ BoardUpdate(schema)      body 검사 (title 길이 등)        실패 → 422
  ├─ Depends(get_db)          DB 세션 하나 열기
  └─ Depends(get_current_user)  ── core/dependencies.py
        ├─ HTTPBearer         헤더에서 토큰 꺼내기             없음 → 401
        ├─ verify_access_token (utils/security.py)
        │     jwt.decode       서명·만료 검사                  실패 → UserCredentialsException → 401
        └─ db.get(User, sub)  토큰 주인 찾기 → current_user
  │
  ▼
services/board.update(db, id, data, user_id=current_user.user_id)
  ├─ 글 없음                → BoardNotFoundException   → router가 404
  ├─ 글쓴이 ≠ current_user  → BoardPermissionException → router가 403
  └─ 수정 후 commit
  │
  ▼
{"message": "3번이 수정되었습니다."}
```

### 1-6. API 목록 (현재 기준)

| 메서드 | 경로 | 인증 필요 | 설명 |
| :--- | :--- | :---: | :--- |
| POST | `/auth` | | 회원가입 |
| POST | `/auth/login` | | 로그인 → `access_token` 발급 |
| PATCH | `/auth/{user_id}/name` · `/email` · `/password` | ⚠️ 아직 없음 | 회원정보 수정 |
| GET | `/boards?page=&size=` | | 전체 목록 (페이지네이션) |
| GET | `/boards/recents` | | 최신 4개 |
| GET | `/boards/{id}` | | 상세 (작성자, 댓글 포함) |
| POST | `/boards` | ✅ | 작성 (작성자 = 토큰 주인) |
| PUT | `/boards/{id}` | ✅ 본인만 | 수정 |
| DELETE | `/boards/{id}` | ✅ 본인만 | 삭제 |
| POST · PUT · DELETE | `/comments…` | ⚠️ 아직 없음 | 댓글 (다음 수업 예상) |

---

## 2부. 보안 개념

### 2-1. 인증(Authentication) vs 인가(Authorization)

| | 인증 | 인가 |
| :--- | :--- | :--- |
| 질문 | **너 누구야?** | **너 이거 해도 돼?** |
| 실패 시 | **401** Unauthorized | **403** Forbidden |
| 이 프로젝트 | 로그인, `get_current_user` | `board.user_id != current_user.user_id` 검사 |

이름이 헷갈리지만 401은 "인증 안 됨(누군지 모름)", 403은 "누군지는 아는데 권한 없음"입니다.

### 2-2. 비밀번호 해싱: `core/security.py`

```python
password_hash = PasswordHash.recommended()   # Argon2

has_password("Abcd123!")             # → "$argon2id$v=19$m=...$..." (DB에 저장)
verify_password("Abcd123!", 해시)    # → True / False
```

- **해싱은 단방향**입니다. 해시에서 원래 비밀번호를 되돌릴 수 없습니다. 암호화(복호화 가능)와 다릅니다.
- 그래서 로그인은 "입력값을 다시 해시해서 비교"하는 방식으로 동작하고, `verify_password`가 이 일을 합니다.
- 같은 비밀번호도 매번 해시가 다릅니다. **솔트(salt)**라는 랜덤 값이 섞이기 때문입니다. 해시 문자열 안에 솔트가 들어 있어 검증은 가능합니다.
- DB가 털려도 원래 비밀번호는 알 수 없습니다. Argon2는 일부러 느리게 만든 알고리즘이라 무차별 대입 공격도 어렵습니다.

**`DUMMY_HASH`와 Timing Attack 방지 (`services/user.py`)**

```python
if existing_user is None:
    verify_password(data.password, DUMMY_HASH)   # 일부러 시간 쓰기
    raise UserNotFoundException
```

- 없는 이메일이면 바로 응답하고, 있는 이메일이면 Argon2 검증에 시간이 걸린다고 해 봅시다.
- 그러면 **응답 속도만 보고 가입된 이메일인지 알아낼 수 있습니다.**
- 그래서 없는 이메일일 때도 가짜 해시로 검증을 한 번 해서 걸리는 시간을 맞춥니다.
- 같은 이유로 실패 응답 메시지도 "이메일 또는 비밀번호가 올바르지 않습니다."로 **통일하는 것이 좋습니다**(현재는 이메일/비밀번호가 따로 표시됨).

### 2-3. JWT (JSON Web Token)

로그인에 성공하면 서버가 **서명된 출입증**을 발급합니다. 이후 요청마다 이 출입증을 보여줍니다.

```text
eyJhbGciOiJIUzI1NiJ9 . eyJzdWIiOiIxIiwiZXhwIjoxNzkx...} . 3kD9fX...
└────── Header ──────┘ └──────────── Payload ────────────┘ └ Signature ┘
  알고리즘(HS256)          {"sub": "1", "exp": 1791272419}    SECRET_KEY로 만든 서명
```

| 부분 | 내용 | 주의 |
| :--- | :--- | :--- |
| Header | 서명 알고리즘 | |
| Payload | `sub`(사용자 id), `exp`(만료시각) | **암호화가 아니라 base64 인코딩**이라 누구나 읽을 수 있음 → 비밀번호 같은 민감정보 넣지 말 것 |
| Signature | Header+Payload를 `SECRET_KEY`로 서명한 값 | 내용을 한 글자라도 바꾸면 서명이 안 맞아 검증 실패 |

**토큰 만들기: `create_access_token`**
```python
to_encode = {"sub": str(user.user_id)}          # sub는 문자열 규칙
to_encode["exp"] = datetime.now(timezone.utc) + timedelta(seconds=3600)  # 1시간
jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
```

**토큰 검증: `verify_access_token`**
```python
jwt.decode(token, settings.secret_key, algorithms=["HS256"])
# 서명 불일치 / 만료(exp 지남) / 형식 오류 → InvalidTokenError → UserCredentialsException
```

**알아둘 점**
- `exp`는 `jwt.decode`가 **자동으로 검사**합니다. 직접 비교할 필요가 없습니다.
- `sub`는 문자열이라서 DB 조회 시 `int(user_id)`로 바꿉니다.
- 시간은 `datetime.now(timezone.utc)`(또는 `datetime.now(UTC)`)를 씁니다. `datetime.utcnow()`는 deprecated입니다.

### 2-4. `SECRET_KEY`

```bash
openssl rand -hex 32     # (open 아님!) 실행할 때마다 새 랜덤값
```

- **한 번 생성해서 `.env`에 저장하고 계속 같은 값을 씁니다.**
- 키를 바꾸면 기존에 발급한 모든 토큰이 서명 불일치로 무효가 됩니다(전원 재로그인).
- 키가 유출되면 누구나 아무 `sub`로 토큰을 위조할 수 있습니다. 그래서 코드에 쓰지 않고 `.env`에 넣으며, `.env`는 `.gitignore`에 들어 있습니다.
- `core/config.py`의 `Settings`가 `.env`에서 `SECRET_KEY`를 읽어 `settings.secret_key`로 제공합니다.

### 2-5. Bearer 인증과 `HTTPBearer`

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIi...
```

"Bearer"는 **이 토큰을 가진(bear) 사람을 인정해 달라**는 뜻입니다. 그래서 토큰이 유출되면 그대로 도용될 수 있습니다. 만료시간(`exp`)을 두는 이유가 이것입니다.

**`HTTPBearer` vs `OAuth2PasswordBearer`**

| | `HTTPBearer` (지금 사용) | `OAuth2PasswordBearer` (공식 문서) |
| :--- | :--- | :--- |
| 로그인 요청 형식 | JSON `{email, password}` 그대로 | form-data, 필드명 `username` |
| Swagger Authorize | 토큰을 직접 붙여넣기 | 아이디/비번 입력하면 자동 로그인 |
| 꺼내는 값 | `credentials.credentials` | `token` 문자열 바로 |
| 헤더 없을 때 | 401 (FastAPI 0.141 기준, 예전 버전은 403) | 401 |

React에서 JSON으로 로그인하기 편해서 `HTTPBearer`를 쓴 것으로 보입니다. 두 방식 모두 결국 `Authorization: Bearer <토큰>` 헤더를 읽는다는 점은 같습니다.

### 2-6. `get_current_user`와 `Depends`

```python
security = HTTPBearer()

def get_current_user(credentials = Depends(security), db = Depends(get_db)):
    payload = verify_access_token(credentials.credentials)   # 토큰 검사
    user_id = payload.get("sub")
    if user_id is None:
        raise UserCredentialsException
    user = db.get(User, int(user_id))
    if user is None:
        raise UserNotFoundException
    return user
```

- 라우터에 `current_user: User = Depends(get_current_user)`라고 **한 줄만 쓰면** 그 API는 로그인 필수가 됩니다.
- 의존성이 의존성을 부르는 구조(`get_current_user` → `HTTPBearer`, `get_db`)이고, FastAPI가 순서대로 실행해 줍니다.
- 역할 분리:
  - `utils/security.py`: JWT만 다룸 (FastAPI 몰라도 됨)
  - `core/dependencies.py`: FastAPI와 연결하는 지점 (`Depends`)
  - `exceptions/`: 문제 이름

**왜 `main.py`에 `exception_handler`가 필요한가**
의존성 안에서 발생한 예외는 라우터 함수의 `try/except`에 **들어가기 전**에 터집니다. 라우터에서 잡을 수 없으니, 처리하지 않으면 500이 납니다. 그래서 앱 전체에 등록해 둡니다.

```python
@app.exception_handler(UserCredentialsException)
async def credentials_handler(request, exc):
    return JSONResponse(status_code=401,
                        content={"detail": "인증 정보가 유효하지 않습니다."},
                        headers={"WWW-Authenticate": "Bearer"})
```

### 2-7. 인가: "본인 글만"

```python
# services/board.py
if target_board is None:
    raise BoardNotFoundException          # 먼저 존재 확인 → 404
if target_board.user_id != user_id:
    raise BoardPermissionException        # 그다음 주인 확인 → 403
```

**핵심 원칙: 누가 요청했는지는 클라이언트가 보낸 값이 아니라 토큰으로 판단합니다.**

| 수정 전 | 수정 후 |
| :--- | :--- |
| `BoardCreate`에 `user_id` 있음 → 아무 id나 넣어 남인 척 작성 가능 | `user_id` 제거, `current_user.user_id` 사용 |
| `/auth/{user_id}/name` → 남의 id로 정보 변경 가능 | `/auth/me/...` + `current_user` (예정) |
| 댓글 `CommentCreate.user_id` | 제거하고 토큰 사용, `board_id`는 유지 (예정) |

`board_id`는 "어느 글에 다는가"라서 토큰으로 알 수 없으니 계속 요청에서 받습니다.

### 2-8. 상태코드 정리

| 코드 | 의미 | 이 프로젝트에서 나오는 경우 |
| :--- | :--- | :--- |
| 400 | 잘못된 요청 | 기존과 같은 비밀번호로 변경 |
| 401 | 인증 실패 | 로그인 실패, 토큰 없음·위조·만료 |
| 403 | 권한 없음 | 남의 글 수정/삭제 |
| 404 | 없음 | 게시글/댓글/유저 없음 |
| 409 | 충돌 | 이미 가입된 이메일 |
| 422 | 형식 오류 | Pydantic 검사 실패 (비밀번호 규칙, 빈 제목 등) |
| 500 | 서버 오류 | 처리하지 않은 예외 → **나오면 코드 버그** |

### 2-9. 전체 로그인 흐름

```text
[회원가입]  POST /auth {email, password, name}
            → 비밀번호 규칙 검사(schema) → Argon2 해시 → DB 저장

[로그인]    POST /auth/login {email, password}
            → 이메일로 유저 찾기 → verify_password
            → create_access_token({"sub": "1"}) → {"access_token": "...", "token_type": "bearer"}

[프론트]    토큰 저장 (localStorage 등)
            이후 모든 요청 헤더에 Authorization: Bearer <토큰>

[보호 API]  get_current_user → 토큰 검증 → current_user
            → services에서 본인 확인 → 처리

[만료]      1시간 후 jwt.decode가 거부 → 401 → 프론트는 로그아웃 처리 후 재로그인 유도
```

---

## 3부. 남은 할 일 체크리스트

**백엔드**
- [ ] 댓글: `CommentCreate`에서 `user_id` 제거, 3개 API에 `get_current_user`, 본인 확인 + `CommentPermissionException`(403)
- [ ] 회원정보 수정 API를 `{user_id}` 경로에서 `current_user` 방식으로 변경 (`/auth/me`)
- [ ] `get_current_user`의 `UserNotFoundException`(토큰은 정상이지만 탈퇴한 유저)도 `exception_handler`나 `HTTPException`으로 처리. 지금은 500
- [ ] 로그인 실패 메시지와 상태코드 통일 (401 + 같은 문구)
- [ ] (선택) 댓글 작성 시 없는 `board_id`면 404 (지금은 FK 오류로 500)

**프론트엔드 (`frontend/reactsource/simple-board-app`)**
- [ ] 로그인/회원가입 페이지
- [ ] 토큰 저장 (`simple-auth-app`의 Context 또는 `simple-auth-app2`의 Redux 방식 참고)
- [ ] axios interceptor로 `Authorization: Bearer` 자동 첨부
- [ ] 하드코딩된 `user_id: 1` 제거 (`BoardForm.tsx`, `BoardDetail.tsx`, `types/board.ts`)
- [ ] 본인 글에만 수정/삭제 버튼 표시, 401이면 로그아웃
