from pydantic import BaseModel

class TaskCreate(BaseModel):
    text:str
    done:bool

class Task(TaskCreate):
    id:int

class TaskResponse(TaskCreate):
    id:int

class TaskPageResponse(BaseModel):
    items:list[TaskResponse]
    total:int
    total_pages:int
    page:int
    size:int

class TaskUpdate(BaseModel):
    text:str|None = None
    done:bool|None = None


# const initialTasks: TaskProps[] = [
#   { id: 0, text: "Visit Kafka Museum", done: true },
#   { id: 1, text: "Watch a puppet show", done: false },
#   { id: 2, text: "Lennon Wall pic", done: false },
# ];