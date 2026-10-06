# 처음 배우는 API · REST API · FastAPI

> 내 할 일(todo) 프로젝트로 이해하는 입문 노트 · 2026-09-21  
> VS Code에서 이 파일을 열고 **Cmd + Shift + V**를 누르면 미리보기로 읽을 수 있습니다.

이 문서는 API를 처음 접하는 사람을 위한 설명입니다. 앞부분에서 개념을 익히고, 뒷부분에서 현재 프로젝트와 연결합니다. 설명용 코드는 실제 파일에 자동으로 반영되지 않습니다.

## 1. API는 무엇인가?

**API는 다른 프로그램의 기능이나 데이터를 사용할 수 있도록 정해 둔 호출 방법과 약속입니다.**

예를 들어 할 일 화면에서 삭제 버튼을 눌렀다고 생각해 봅시다. 화면을 만드는 React가 서버 안의 데이터를 직접 지우는 것은 아닙니다. 서버에 “1번 할 일을 삭제해 주세요”라는 요청을 보내고, 서버가 처리한 결과를 받습니다.

```text
사용자: 삭제 버튼 클릭
  ↓
React: DELETE /todos/1 요청 전송
  ↓
서버: 1번 할 일을 찾아 삭제
  ↓
서버: 처리 결과 응답
  ↓
React: 응답을 확인하고 화면 갱신
```

이때 어떤 주소로, 어떤 방식으로, 어떤 데이터를 보내야 하는지 정한 것이 API의 약속입니다. 화면과 서버를 서로 다른 언어로 만들어도 이 약속을 따르면 통신할 수 있습니다.

API가 모두 인터넷 통신을 사용하는 것은 아닙니다. 라이브러리의 함수도 API가 될 수 있습니다. 여기서는 **HTTP로 요청과 응답을 주고받는 웹 API**를 배웁니다.

## 2. 먼저 구분할 단어

| 단어 | 의미 | 이 프로젝트의 예 |
| :--- | :--- | :--- |
| 클라이언트 | 요청을 보내는 프로그램 | 브라우저, React 앱, Swagger UI |
| 서버 | 요청을 받아 처리하고 응답하는 프로그램 | 실행 중인 FastAPI 앱과 웹 서버 |
| 프론트엔드 | 사용자가 보고 조작하는 화면 쪽 | React의 할 일 목록과 버튼 |
| 백엔드 | 데이터 처리와 업무 규칙을 담당하는 쪽 | 할 일 조회·등록·수정·삭제 코드 |
| HTTP | 웹에서 요청과 응답을 주고받는 통신 규칙 | GET 요청, 200 응답 |
| JSON | 데이터를 텍스트로 표현하는 형식 | `{"id": 1, "title": "공부"}` |
| 엔드포인트 | API 기능에 접근하는 지점 | 이 문서에서는 `GET /todos/1`처럼 메서드와 경로로 구분 |
| 데이터베이스(DB) | 데이터를 저장하고 조회하는 시스템 | 현재 실습에서는 아직 사용하지 않음 |

서버를 반드시 별도 컴퓨터에 설치해야 하는 것은 아닙니다. 지금은 내 컴퓨터에서 서버와 브라우저를 함께 실행하며 실습할 수 있습니다.

## 3. API, REST API, FastAPI는 어떻게 다른가?

| 개념 | 무엇인가? | 기억할 표현 |
| :--- | :--- | :--- |
| API | 프로그램 사이의 사용 약속 | “어떻게 요청하고 무엇을 받는가” |
| REST | 자원을 중심으로 시스템을 설계하는 아키텍처 스타일 | “무엇을 대상으로 어떤 작업을 하는가” |
| REST API | REST 원칙에 맞춰 설계한 API | `/todos/1`이라는 자원을 GET·PUT·DELETE로 다룸 |
| FastAPI | Python으로 웹 API를 만드는 프레임워크 | 위 약속을 실제 코드로 구현하는 도구 |

**FastAPI와 REST API는 경쟁하는 도구가 아닙니다. FastAPI로 REST 스타일의 API를 만들 수 있습니다.** FastAPI를 쓴다고 모든 설계가 자동으로 REST가 되는 것은 아닙니다.

REST에서 자원(resource)은 다루려는 대상입니다. 할 일 앱에서는 할 일, 쇼핑몰에서는 상품과 주문, 게시판에서는 게시글과 댓글이 자원입니다.

REST는 단순히 “URL에 명사를 쓰기”만을 뜻하지는 않습니다. 클라이언트와 서버의 역할 분리, 일관된 인터페이스, 무상태성, 캐시 등 여러 제약을 포함합니다. 처음에는 자원과 HTTP 메서드를 연결하는 데 집중하면 됩니다.

여기서 **무상태성**은 “서버에 데이터를 저장하지 않는다”는 뜻이 아닙니다. 각 요청을 이해하는 데 필요한 정보를 해당 요청이 제공해야 한다는 뜻입니다. 서버는 DB에 할 일 데이터를 저장할 수 있습니다.

## 4. HTTP 요청은 무엇으로 이루어질까?

할 일을 수정하는 요청을 예로 들면 다음과 같습니다.

```http
PUT /todos/1 HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "id": 1,
  "title": "FastAPI 복습",
  "completed": true,
  "important": false
}
```

| 부분 | 역할 |
| :--- | :--- |
| `PUT` | 어떤 작업을 요청하는지 나타내는 메서드 |
| `/todos/1` | 어느 자원을 대상으로 하는지 나타내는 경로 |
| `Host` | 요청할 서버 주소 |
| `Content-Type` | 본문 데이터의 형식을 알려 주는 헤더 |
| 아래 JSON | 수정할 데이터를 담은 요청 본문(body) |

모든 요청에 본문이 필요한 것은 아닙니다. 단순한 조회는 보통 경로와 쿼리만으로 필요한 정보를 전달합니다.

서버의 응답에도 **상태 코드, 헤더, 본문**이 있습니다. 서버는 결과 데이터를 JSON으로 보내고, 클라이언트는 그 데이터를 이용해 화면을 만듭니다. 서버가 JSON을 반환했다고 React 화면이 저절로 바뀌는 것은 아닙니다. React에서 응답을 받아 상태를 갱신하거나 다시 조회해야 합니다.

## 5. URL을 읽는 법

```text
http://127.0.0.1:8000/todos/get?id=1
└─┬─┘  └───┬───┘ └┬┘└───┬────┘└─┬─┘
  방식     호스트   포트    경로    쿼리
```

- `http`: 통신 방식입니다. `https`는 통신을 암호화합니다.
- `127.0.0.1`: 요청을 보내는 컴퓨터 자신을 가리킵니다.
- `8000`: 같은 컴퓨터에서 어떤 서비스로 보낼지 구분하는 포트입니다.
- `/todos/get`: 서버가 기능을 찾을 때 사용하는 경로입니다.
- `?id=1`: 추가로 전달하는 쿼리 매개변수입니다.

쿼리가 여러 개라면 `?`는 처음에 한 번만 쓰고, 뒤에는 `&`로 연결합니다.

```text
/todos/?completed=false&important=true
```

주소에 조건을 붙였다는 이유만으로 서버가 필터링하는 것은 아닙니다. 서버에도 그 값을 받고 필터링하는 코드가 있어야 합니다.

## 6. GET · POST · PUT · PATCH · DELETE

CRUD는 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)를 묶어서 부르는 말입니다.

| 메서드 | 대표 목적 | 할 일 API 설계 예시 |
| :--- | :--- | :--- |
| GET | 조회 | `GET /todos/`: 목록 조회 |
| GET | 하나 조회 | `GET /todos/1`: 1번 조회 |
| POST | 새 데이터 생성 또는 처리 요청 | `POST /todos/`: 할 일 등록 |
| PUT | 대상 자원의 표현을 전체 교체 | `PUT /todos/1`: 수정 가능한 필드 전체 전달 |
| PATCH | 일부 변경 | `PATCH /todos/1`: 완료 여부만 변경 |
| DELETE | 삭제 | `DELETE /todos/1`: 1번 삭제 |

위 표는 학습용 설계 예시이며, 현재 프로젝트에 모든 경로가 구현되어 있다는 뜻은 아닙니다. HTTP 메서드 의미는 [MDN의 메서드 설명](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)에서 확인할 수 있습니다.

`GET /todos/1`과 `DELETE /todos/1`은 주소가 같아도 서로 다른 작업입니다. **경로와 메서드를 함께 봐야 합니다.** 브라우저 주소창에 주소를 입력하는 것은 일반적으로 GET 요청이므로, 주소창만으로 PUT이나 DELETE를 테스트할 수는 없습니다.

또한 `@...delete(...)`라고 선언하는 것만으로 데이터가 삭제되지는 않습니다. 개발자가 함수 안에서 삭제 코드를 작성해야 합니다.

## 7. 경로 · 쿼리 · 본문: 값을 전달하는 세 가지 위치

### 7-1. 경로 매개변수: 어떤 항목인가?

```python
@todo_router.get("/{id}")
async def get_todo(id: int):
    return {"received_id": id}
```

라우터의 접두사가 `/todos`라면 `/todos/1`로 요청합니다. FastAPI는 `{id}` 자리에 온 `1`을 읽고 정수로 변환하여 함수의 `id`에 전달합니다. `/todos/abc`라면 정수로 해석할 수 없으므로 검증 오류가 발생합니다.

### 7-2. 쿼리 매개변수: 어떤 조건인가?

```python
@todo_router.get("/get")
async def get_query_todo(id: int):
    return {"received_id": id}
```

이 경우 요청 주소는 `/todos/get?id=1`입니다. 경로에 `{id}`가 없고 함수에는 단순 타입인 `id: int`가 있으므로 FastAPI는 기본적으로 쿼리에서 값을 받습니다. 함수 이름에 `query`가 있어서 그런 것은 아닙니다.

`id: int`에는 기본값이 없으므로 이 예시에서 `id`는 필수입니다. 생략하면 검증 오류가 납니다. 다음처럼 기본값을 주면 생략할 수도 있습니다.

```python
@todo_router.get("/get")
async def get_query_todo(id: int | None = None):
    return {"received_id": id}
```

`int | None`은 정수 또는 `None`을 뜻하고, `= None`은 값이 오지 않았을 때 사용할 기본값입니다. 자세한 규칙은 [FastAPI 쿼리 매개변수 설명](https://fastapi.tiangolo.com/tutorial/query-params/)을 참고하세요.

### 7-3. 요청 본문: 어떤 내용을 저장할까?

```python
class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool
    important: bool


@todo_router.put("/{todo_id}")
async def put_todo(todo_id: int, update_todo: TodoItem):
    return {"target_id": todo_id, "received_data": update_todo}
```

`PUT /todos/1`로 요청하며 본문에는 JSON 객체를 보냅니다.

```json
{
  "id": 1,
  "title": "API 공부",
  "completed": false,
  "important": true
}
```

`todo_id`는 경로에서, `update_todo`는 본문에서 받습니다. Pydantic 모델로 선언한 매개변수를 FastAPI가 본문 데이터로 해석하기 때문입니다. 일반적인 단일 모델 본문에서는 `{"update_todo": {...}}`로 한 번 더 감싸지 않습니다. [FastAPI 요청 본문 설명](https://fastapi.tiangolo.com/tutorial/body/)

**경로의 `todo_id`와 본문의 `id`는 별개의 값입니다.** FastAPI가 둘이 같다고 자동으로 검사해 주지는 않습니다. 현재 모델은 본문의 `id`도 필수이므로 생략하면 422가 납니다. 실무에서는 수정용 모델에서 `id`를 빼고 대상 ID는 경로로만 받도록 설계하기도 합니다.

| 선언 | 기본적으로 받는 위치 |
| :--- | :--- |
| 경로의 `{todo_id}`와 일치하는 매개변수 | 경로 |
| 경로에 없는 단순 타입 매개변수 | 쿼리 |
| Pydantic 모델 타입 매개변수 | 요청 본문 |

이 표는 현재 예제의 기본 규칙입니다. 나중에는 `Query`, `Body`, `Header`, `Cookie` 등으로 위치와 검증 조건을 명시할 수도 있습니다.

## 8. Pydantic은 무엇을 해 주는가?

Pydantic 모델은 **받을 데이터의 모양과 타입을 선언하고, 입력을 검사하는 도구**입니다.

```python
class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool
    important: bool
```

이 선언은 네 필드가 필요하다는 뜻입니다. FastAPI는 요청 본문을 이 모델로 검증한 뒤 함수에 전달합니다. 기본 설정에서는 `"1"`처럼 변환 가능한 입력을 정수로 바꾸기도 하므로, 타입 선언이 항상 “다른 타입을 무조건 거절한다”는 뜻은 아닙니다.

JSON과 Python 문법도 구분해야 합니다.

| 위치 | 예시 |
| :--- | :--- |
| JSON 본문 | `{"completed": true}` |
| Python 딕셔너리 | `{"completed": True}` |
| Python 객체 생성 | `TodoItem(id=1, title="공부", completed=True, important=False)` |

JSON의 불리언은 `true/false`, Python에서는 `True/False`입니다. 딕셔너리에서 키와 값은 `:`로 연결하지만, 함수 호출의 이름 붙은 인자는 `=`로 전달합니다.

모델은 데이터베이스가 아닙니다. 모델 객체를 만들었다고 파일이나 DB에 자동 저장되지 않습니다.

## 9. 내 프로젝트 파일은 어떻게 연결되는가?

```text
todo/main.py
  app = FastAPI()
  app.include_router(todo_router)
          │ 경로 등록
          ▼
todo/routes/todo.py
  APIRouter(prefix="/todos")
  GET /, GET /get, POST /{todo_id}, PUT /{todo_id}, DELETE /{todo_id}
          │ 데이터 타입 사용
          ▼
todo/models/model.py
  TodoItem: id, title, completed, important
```

- [main.py](todo/main.py): 앱을 만들고 라우터를 연결하는 시작점입니다.
- [routes/todo.py](todo/routes/todo.py): 주소별로 실행할 함수와 할 일 처리 코드를 모읍니다.
- [models/model.py](todo/models/model.py): 요청 데이터의 구조를 정의합니다.

이 지도는 문서를 작성할 때 저장된 코드를 기준으로 합니다. 이때 `GET /{id}`는 주석 처리되어 있습니다.

### 데코레이터는 함수를 경로에 등록한다

```python
@todo_router.get("/")
async def get_todos():
    return {"todos": todo_items}
```

`@todo_router.get("/")`는 “이 경로로 GET 요청이 오면 아래 함수를 실행한다”는 등록입니다. 라우터의 `/todos`와 함수의 `/`를 합쳐 최종 경로는 `/todos/`가 됩니다.

서버 시작 시 모듈이 로드되면서 목록과 함수가 준비되고 경로가 등록됩니다. 그 뒤 요청이 올 때 해당 함수 본문이 실행됩니다. 함수 이름이 URL이 되는 것은 아닙니다.

`async def`는 비동기 함수 선언입니다. 네트워크 작업 등을 `await`로 기다리는 동안 다른 작업을 처리할 수 있게 하는 데 사용합니다. 붙였다고 모든 코드가 자동으로 빨라지거나 느린 작업이 사라지는 것은 아닙니다.

## 10. `todos`와 `todo_items`는 왜 둘 다 있을까?

```python
todo_items = [TodoItem(**todo) for todo in todos]
```

이 코드는 `todos`의 딕셔너리를 하나씩 읽어 `TodoItem` 객체를 만들고, 새 목록에 넣습니다. `**todo`는 딕셔너리의 키와 값을 이름 붙은 인자로 풀어 전달합니다.

| 변수 | 들어 있는 값 | 접근 방법 |
| :--- | :--- | :--- |
| `todos` | 딕셔너리 | `todo["id"]` |
| `todo_items` | `TodoItem` 객체 | `todo.id` |

두 목록은 자동 동기화되지 않습니다. 현재처럼 숫자·문자열·불리언 필드로 만든 모델을 수정해도 원래 딕셔너리는 바뀌지 않습니다. `todo_items`에서 항목을 삭제해도 `todos`에서는 삭제되지 않습니다.

이 실습에서는 `todos`를 초기 데이터로만 사용하고, **GET·POST·PUT·DELETE가 모두 `todo_items`를 다루도록 맞추면** 이해하기 쉽습니다. 꼭 두 목록을 만들어야 하는 것은 아닙니다. 처음부터 `TodoItem(...)` 객체들로 목록을 만들어도 됩니다.

이 목록은 현재 실행 중인 Python 프로세스의 메모리에만 있습니다. 서버가 재시작되면 초기 코드대로 다시 만들어집니다. 개발 서버가 파일 변경으로 자동 재시작되어도 수정한 데이터가 사라질 수 있습니다. 영구 보관하려면 별도의 저장소가 필요합니다.

## 11. 지금 코드에서 헷갈렸던 부분

### A. `/get`과 `/{id}`의 순서

고정 경로 `/get`은 동적 경로 `/{id}`보다 먼저 선언하세요. 반대 순서라면 `/todos/get`의 `get`이 `{id}`에 잡혀 정수 변환 오류가 날 수 있습니다. 현재는 `/{id}`가 주석 처리되어 있지만, 다시 활성화할 때 순서에 주의하세요. [FastAPI 경로 순서 설명](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters)

```python
# 고정 경로 먼저
@todo_router.get("/get")
async def get_query_todo(id: int):
    ...


# 동적 경로 나중에
@todo_router.get("/{id}")
async def get_todo(id: int):
    ...
```

위의 `...`는 설명에서 생략한 부분입니다. 완성된 함수로 붙여 넣으라는 의미는 아닙니다.

### B. `/todos/?id=1`과 `/todos/get?id=1`은 다르다

현재 쿼리 조회 함수는 `@todo_router.get("/get")`이므로 `/todos/get?id=1`로 호출합니다. `/todos/?id=1`은 `@todo_router.get("/")`에 도달합니다. 현재 그 함수에는 `id` 처리 코드가 없으므로 전체 목록이 반환됩니다.

`?id=1`을 붙인다고 FastAPI가 자동으로 ID 검색을 수행하지 않습니다. FastAPI는 값을 전달하고 검증하며, 실제 검색은 우리가 작성한 `for`와 `if`가 담당합니다.

### C. 왜 조회 함수를 두 개 만들까?

같은 ID로 조회하는 기능을 두 개 만들 의무는 없습니다. 현재는 경로와 쿼리 전달 방식을 각각 연습하는 예제로 이해하면 됩니다. 일반적인 설계에서는 `/todos/1`로 특정 항목을 조회하고, `/todos/?completed=false`로 조건에 맞는 목록을 조회하는 식으로 역할을 나눌 수 있습니다.

### D. POST 경로에 사용하지 않는 `{todo_id}`가 있다

현재 코드는 `@todo_router.post("/{todo_id}")`인데 함수는 `todo_id`를 받거나 사용하지 않습니다. 따라서 URL의 ID가 본문의 ID를 결정해 주는 구조가 아닙니다. 새 항목을 추가하는 이 예제라면 `@todo_router.post("/")`가 더 자연스럽습니다. 이는 설명이며 실제 파일은 수정하지 않았습니다.

### E. 항목 하나와 전체 목록을 구분한다

반복문의 `todo`는 현재 항목 하나이고, `todo_items`는 전체 목록입니다. 한 항목 조회나 수정 결과는 `{"todo": todo}`, 목록 조회 결과는 `{"todos": todo_items}`처럼 이름을 맞추면 읽기 쉽습니다. 키 이름이 단수·복수라고 동작이 바뀌지는 않으며, 실제 전달하는 값이 중요합니다.

## 12. 상태 코드로 성공과 실패를 읽자

| 코드 | 의미 | 예시 |
| :--- | :--- | :--- |
| 200 | 성공 | 조회·수정 성공 |
| 201 | 새 자원 생성 성공 | 새 할 일 등록 |
| 204 | 성공했고 응답 본문 없음 | 본문을 보내지 않는 삭제 응답 |
| 404 | 요청한 자원을 찾지 못함 | 없는 ID 조회 |
| 405 | 해당 경로에서 메서드를 허용하지 않음 | GET만 있는 경로에 DELETE 요청 |
| 422 | 입력 검증 실패 | 필수 필드 누락, 정수 자리에 해석 불가능한 문자 |
| 500 | 서버 내부 오류 | 처리 중 예상하지 못한 예외 |

이 코드는 [HTTP 상태 코드](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)의 대표 예시입니다. 422는 FastAPI의 기본 요청 검증에서 흔히 보게 됩니다.

현재 코드처럼 다음 문장을 반환하면 기본적으로 HTTP 상태는 **200**입니다.

```python
return {"todo": "todo를 찾을 수 없습니다."}
```

오류라는 글자를 썼다고 HTTP 오류가 되지는 않습니다. 없는 항목을 404로 알리려면 다음처럼 작성할 수 있습니다.

```python
raise HTTPException(status_code=404, detail="todo를 찾을 수 없습니다.")
```

`return`은 정상 응답 값을 돌려주고, `raise`는 예외를 발생시킵니다. FastAPI는 `HTTPException`을 해당 상태 코드의 응답으로 처리합니다. [FastAPI 오류 처리 설명](https://fastapi.tiangolo.com/tutorial/handling-errors/)

응답이 이상하면 “렉이 걸린다”로 묶기보다 다음을 확인하세요.

1. 요청을 보낸 메서드와 전체 URL이 맞는가?
2. 응답이 아예 없는가, 아니면 422나 500이 왔는가?
3. 응답 본문의 `detail`에 어떤 필드와 위치가 나오는가?
4. 서버 터미널에 예외가 출력되는가?
5. 코드 수정이 저장되었고 서버가 새 코드를 읽었는가?

예를 들어 `loc: ["path", "id"]`는 경로의 ID, `["body", "id"]`는 본문의 ID, `["query", "id"]`는 쿼리의 ID 문제라는 단서입니다.

## 13. 내 프로젝트를 `/docs`에서 직접 실습하기

현재 프로젝트의 가상환경에는 FastAPI가 설치되어 있습니다. 새로운 터미널에서 다음과 같이 실행할 수 있습니다. 이미 같은 포트로 서버를 실행 중이라면 중복 실행하지 말고 기존 서버를 사용하세요.

```bash
cd /Users/sanghyeun/academy/fastapi_source/todo
../.venv/bin/python -m uvicorn main:app --reload
```

`main:app`은 `main.py` 안의 `app` 객체를 의미합니다. Uvicorn은 HTTP 요청을 받아 FastAPI 앱으로 전달하는 웹 서버이고, `--reload`는 코드 변경 시 서버를 다시 시작하는 개발용 옵션입니다. 현재 import 구조에 맞춰 `todo` 폴더에서 실행합니다.

브라우저에서 `http://127.0.0.1:8000/docs`를 열면 API를 직접 호출할 수 있는 Swagger UI가 나옵니다. 이것도 서버에 요청을 보내는 클라이언트입니다. 화면은 FastAPI가 생성한 OpenAPI 명세를 사용합니다. [FastAPI 첫 단계 설명](https://fastapi.tiangolo.com/tutorial/first-steps/)

각 항목을 펼쳐 **Try it out → 값 입력 → Execute** 순서로 사용합니다. Request URL, Response code, Response body를 함께 확인하세요.

현재 저장된 코드를 기준으로 다음을 실습해 보세요.

1. `GET /todos/`로 처음 목록을 확인합니다.
2. `GET /todos/get`의 `id`에 `1`을 넣습니다. Request URL에 `?id=1`이 붙는지 봅니다.
3. `PUT /todos/{todo_id}`의 경로 ID에 `1`을 넣고 아래 본문을 보냅니다.
4. 다시 `GET /todos/`로 제목이 바뀌었는지 확인합니다.
5. `DELETE /todos/{todo_id}`로 `1`을 삭제한 뒤 다시 목록을 조회합니다. 이 단계는 실습 데이터를 실제로 삭제합니다.
6. PUT 본문에서 `id`를 빼 보고 422 응답의 `detail`을 읽습니다.

```json
{
  "id": 1,
  "title": "API의 요청과 응답 이해하기",
  "completed": true,
  "important": false
}
```

현재는 메모리 데이터이므로 서버를 재시작하면 초기 항목이 다시 생깁니다. 실습 중 POST 경로는 현재 `/{todo_id}`이며, 앞 절에서 설명한 것처럼 URL의 ID를 함수가 사용하지 않는다는 점도 관찰해 보세요.

## 14. 이해했는지 확인하는 질문

먼저 답을 가리고 자기 말로 설명해 보세요.

1. FastAPI와 REST API는 각각 무엇인가?
2. `GET /todos/1`과 `DELETE /todos/1`은 무엇이 다른가?
3. `/todos/get?id=1`에서 경로와 쿼리는 어디인가?
4. `id: int`라고만 써도 언제 쿼리에서 값을 받는가?
5. `TodoItem` 객체를 만들면 DB에 저장되는가?
6. `todo_items`에서 삭제하면 원래 `todos`도 바뀌는가?
7. `{"message": "실패"}`를 반환하면 상태 코드도 자동으로 실패가 되는가?
8. 서버에서 수정에 성공하면 React 화면도 자동으로 바뀌는가?

<details>
<summary>답 확인하기</summary>

1. FastAPI는 API를 구현하는 Python 도구이고, REST API는 REST 원칙에 맞춰 설계한 API입니다.
2. 대상 경로는 같지만 HTTP 메서드가 달라 조회와 삭제로 구분됩니다.
3. 경로는 `/todos/get`, 쿼리는 `id=1`입니다.
4. 현재 예제처럼 경로에 `{id}`가 없고 별도 위치 지정도 없는 단순 타입 매개변수일 때입니다.
5. 아닙니다. 모델 객체 생성과 영구 저장은 별개입니다.
6. 아닙니다. 별도로 만든 목록입니다.
7. 아닙니다. 상태 코드를 지정하거나 `HTTPException` 등을 사용해야 합니다.
8. 아닙니다. 프론트엔드에서 응답을 처리하고 상태를 바꾸거나 다시 조회해야 합니다.

</details>

## 15. 다음 학습 순서

먼저 GET·POST·PUT·DELETE를 같은 목록에 적용하고, 경로·쿼리·본문이 각각 어디로 전달되는지 익히세요. 그다음 생성용·수정용 모델 분리, 적절한 상태 코드, DB 저장, React 연결 순서로 확장하면 됩니다. 로그인·인증과 배포는 이 흐름이 익숙해진 뒤 배워도 됩니다.

공식 문서는 [FastAPI 튜토리얼](https://fastapi.tiangolo.com/tutorial/)을 기준으로 필요한 부분부터 읽으면 됩니다. 이 문서의 예제는 현재 프로젝트를 이해하기 위한 학습용이며, 실제 서비스에 필요한 영구 저장·동시성 처리·인증까지 구현한 것은 아닙니다.
