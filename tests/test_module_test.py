from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


def greet(name: str) -> str:
    return "Hello, " + name


def test_greet() -> None:
    assert greet("abc") == "Hello, b"


def add_numbers(a: int, b: int) -> int:
    return a + b


class Model(BaseModel):
    age: int
    first_name: str = "ab"
    middle_name: str = "c"
    last_name: Optional[str] = None
    signup_ts: Optional[datetime] = None
    list_of_ints: List[int]


def test_Model() -> None:
    m = Model(age=42, list_of_ints=[1, 2, 3])
    assert m.middle_name == "c"


if __name__ == "__main__":
    print("print 'Hello, world.'")  # checking if mypy finds error or not
    test_greet()
    print(add_numbers(2, 3))
    test_Model()
