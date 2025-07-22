from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass, field
from queue import Queue

from flask import Flask, render_template, render_template_string
from jinja2 import BaseLoader, Environment, Template


@dataclass
class EventStreamABC(ABC):
    event: str
    template: str

    __queue: Queue | None = field(default=None, init=False)

    def __post_init__(self):
        if self.__queue is None:
            self.__queue = Queue()

    def stream(self) -> Generator[str, None]:
        while not self.__queue.empty():
            message = self.__queue.get_nowait()
            yield message

    def action_stream(self, **kwargs) -> str:
        message = f"event: {self.event}\ndata: {self.render_template(**kwargs)}\n\n"
        self.__queue.put(message)

    @abstractmethod
    def render_template(self, **kwargs) -> str: ...


@dataclass
class EventStream(EventStreamABC):
    _template: Template = field(
        init=False,
    )

    def __post_init__(self):
        super().__post_init__()

        self._template = Environment(loader=BaseLoader(), autoescape=True).from_string(
            self.template
        )

    def render_template(self, **kwargs) -> str:
        html = self._template.render(**kwargs)
        return html.replace("\n", "")


@dataclass
class EventStreamString(EventStreamABC):
    app: Flask = field(init=True)

    def render_template(self, **kwargs) -> str:
        with self.app.app_context():
            html = render_template_string(self.template, **kwargs)
            return html.replace("\n", "")


@dataclass
class EventStreamTemplate(EventStreamABC):
    app: Flask = field(init=True)

    def render_template(self, **kwargs) -> str:
        with self.app.app_context():
            html = render_template(self.template, **kwargs)
            return html.replace("\n", "")
