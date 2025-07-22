from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import IntEnum, auto
from functools import partial
from threading import Thread
from time import sleep, time
from typing import Literal

from flask import Flask
from model import Answer, Question
from repository import PlayerRepository, QuizzRepository


class StatusQuestionEnum(IntEnum):
    NEW = auto()
    REGISTER = auto()
    WAITNG = auto()
    RUNING = auto()
    QUESTION = auto()
    END = auto()


@dataclass
class QuestionService:
    players: PlayerRepository
    quizz: QuizzRepository

    status: StatusQuestionEnum = field(default=StatusQuestionEnum.NEW)
    _current_question: int | None = None
    _start_time: int = 0
    _wait_time: int = 0
    __thread: Thread | None = None
    __question_actions: list[Callable] = field(default_factory=list)
    __answer_graphic_actions: list[Callable] = field(default_factory=list)
    __wait_actions: list[Callable] = field(default_factory=list)
    __score_actions: list[Callable] = field(default_factory=list)
    __end_actions: list[Callable] = field(default_factory=list)

    QUESTION_TIME: int = 30
    SCORE_TIME: int = 10
    PLAYERS_TIME: int = 10
    TOTAL_QUESTIONS: int = 10

    @property
    def remain_time(self) -> int:
        tt = self._start_time + self._wait_time - int(time())
        return tt if tt > 0 else 0

    def waiting_player(self) -> bool:
        return self.status == StatusQuestionEnum.REGISTER

    def get_question(self) -> Question:
        return self.quizz.get_question(self._current_question)

    def start(self) -> None:
        if self.status != StatusQuestionEnum.NEW:
            return

        self.__thread = self.__on_thread(
            actions=[
                partial(self.set_status, StatusQuestionEnum.REGISTER),
                partial(self.__waiting, self.PLAYERS_TIME),
                partial(self.set_status, StatusQuestionEnum.RUNING),
                *self.__start_quizz(),
                partial(self.set_status, StatusQuestionEnum.END),
                self.__run_score_actions,
                partial(self.__waiting, 2),
                partial(self.__runner, self.__end_actions),
            ],
        )
        self.__thread.start()

    def __start_quizz(self) -> list[Callable]:
        actions = []
        for i in range(self.TOTAL_QUESTIONS):
            actions.extend(
                [
                    partial(self.set_status, StatusQuestionEnum.QUESTION),
                    self.__next_question,
                    self.__run_question_actions,
                    partial(self.__waiting, self.QUESTION_TIME),
                    partial(self.set_status, StatusQuestionEnum.RUNING),
                    self.__run_score_actions,
                    partial(self.__waiting, self.SCORE_TIME, False),
                ]
            )
            if i == self.TOTAL_QUESTIONS - 1:
                actions.pop()

        return actions

    def __next_question(self):
        if self._current_question is None:
            self._current_question = 0

        elif self._current_question < self.TOTAL_QUESTIONS:
            self._current_question += 1
        else:
            self.status = StatusQuestionEnum.END

    def add_action(
        self,
        action: Callable,
        event: Literal["question", "graphic", "wait", "score", "end"],
    ) -> None:
        if event == "question" and action not in self.__question_actions:
            self.__question_actions.append(action)
        elif event == "graphic" and action not in self.__answer_graphic_actions:
            self.__answer_graphic_actions.append(action)
        elif event == "wait" and action not in self.__wait_actions:
            self.__wait_actions.append(action)
        elif event == "score" and action not in self.__score_actions:
            self.__score_actions.append(action)
        elif event == "end" and action not in self.__end_actions:
            self.__end_actions.append(action)

    def __run_question_actions(self) -> None:
        question = self.get_question()
        if question is None:
            return

        self.__runner(
            self.__question_actions,
            question=question,
            waiting=self.QUESTION_TIME,
        )

    def __run_score_actions(self) -> None:
        players = self.players.players_by_points()

        self.__runner(
            self.__score_actions,
            players=players,
            current=self._current_question + 1,
            total=self.TOTAL_QUESTIONS,
            status=self.status.name,
        )

    def __runner(self, actions: list[Callable], **kwargs) -> None:
        for act in actions:
            act(**kwargs)

    def __waiting(self, seconds: int, in_wait: bool = True) -> None:
        self._start_time = int(time())
        self._wait_time = seconds if in_wait else 0
        sleep(seconds)

    def __on_thread(self, actions: Iterable[Callable], execute: bool = False) -> Thread:
        thread = Thread(
            target=self.__runner,
            args=(actions,),
            daemon=True,
        )

        if execute:
            thread.start()
        return thread

    def set_status(self, status: StatusQuestionEnum, validator: bool = True) -> None:
        if validator:
            self.status = status

    @property
    def is_end(self) -> bool:
        return self.status == StatusQuestionEnum.END

    def evaluate(self, player: str, answer: Answer) -> Question | None:
        player = self.players.get_player(player)
        if player is None:
            return
        question = self.quizz.get_question(self._current_question)
        if question is None or question.id != answer.question_id:
            return

        is_right = question.check_answer(answer.option)
        multiple_point = self.multiple_point()
        if is_right:
            player.add_point(multiple_point)
        question.add_answer(answer.option)

        self.__on_thread(
            actions=[
                partial(
                    self.__runner,
                    self.__answer_graphic_actions,
                    question=question,
                ),
            ],
            execute=True,
        )
        return question

    def multiple_point(self) -> int:
        if self.remain_time <= 0:
            return 0

        if self.remain_time > self.QUESTION_TIME * 0.95:
            return 4
        elif self.remain_time > self.QUESTION_TIME * 0.85:
            return 3
        elif self.remain_time > self.QUESTION_TIME * 0.50:
            return 2

        return 1

    def init_app(self, app: Flask) -> None:
        app.extensions["question_service"] = self

    def reset(
        self, total: int = 10, qtime: int = 30, stime: int = 10, ptime: int = 10
    ) -> None:
        self.status = StatusQuestionEnum.NEW
        self._current_question = None
        self._start_time = 0
        self._wait_time = 0
        self.__thread = None
        self.__question_actions.clear()
        self.__answer_graphic_actions.clear()
        self.__wait_actions.clear()
        self.players.reset()
        self.quizz.reset(self.TOTAL_QUESTIONS)

        if total > self.quizz.total:
            total = self.quizz.total

        self.QUESTION_TIME = qtime
        self.SCORE_TIME = stime
        self.PLAYERS_TIME = ptime
        self.TOTAL_QUESTIONS = total
