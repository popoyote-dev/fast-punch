from dataclasses import dataclass, field
from random import shuffle
from uuid import uuid4


@dataclass
class Player:
    nickname: str
    avatar: str | None = field(default=None)

    _point: int = 0

    def __hash__(self):
        return hash(self.nickname)

    def add_point(self, point: int):
        self._point += point

    @property
    def total(self) -> int:
        return self._point


@dataclass
class Question:
    statement: str
    answer: str
    options: list[str]
    id: str = field(default_factory=lambda: uuid4().hex)
    __answers: dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.reset_answers()
        shuffle(self.options)

    def check_answer(self, answer: str) -> bool:
        return answer == self.answer

    def add_answer(self, option: str):
        if option in self.__answers:
            self.__answers[option] += 1

    @property
    def random_option(self) -> str:
        list_copy = self.options.copy()
        shuffle(list_copy)
        return list_copy

    @property
    def answers(self) -> dict[str, int]:
        return self.__answers

    def reset_answers(self):
        self.__answers = {option: 0 for option in self.options}


@dataclass
class Answer:
    question_id: str
    option: str


@dataclass
class Avatar:
    file: str
    url: str
    id: str = field(default_factory=lambda: uuid4().hex)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Avatar):
            return self.id == other.id
        return False
