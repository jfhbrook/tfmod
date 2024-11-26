import datetime
from enum import IntEnum
import json
import os
import textwrap
from typing import Literal, Mapping, NoReturn, Optional, Self

from rich import print as pprint

from tfmod.error import Error, Exit


class Level(IntEnum):
    """
    Logging level.
    """

    JSON = 0
    TRACE = 1
    DEBUG = 2
    INFO = 3
    WARN = 4
    ERROR = 5

    @classmethod
    def from_str(cls, level: str) -> "Level":
        return {
            "JSON": cls.JSON,
            "TRACE": cls.TRACE,
            "DEBUG": cls.DEBUG,
            "INFO": cls.INFO,
            "WARN": cls.WARN,
            "ERROR": cls.ERROR,
        }.get(level, cls.TRACE)

    def __str__(self: Self) -> str:
        return {
            self.JSON: "JSON",
            self.TRACE: "TRACE",
            self.DEBUG: "DEBUG",
            self.INFO: "INFO",
            self.WARN: "WARN",
            self.ERROR: "ERROR",
        }[self]


Color = Literal["red"] | Literal["yellow"]
TOP_BAR = "╷"
MIDDLE_BAR = "│"
BOTTOM_BAR = "╵"


class Logger:
    def __init__(self, level: Level) -> None:
        self.level = level

    def timestamp(self) -> str:
        now = datetime.datetime.now()
        ts = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
        tz = now.strftime("%z")

        # Milliseconds instead of microseconds
        return ts[:-3] + tz

    def is_level(self, level: Level) -> bool:
        return self.level.value <= level.value

    def log(self, level: Level, message: str) -> None:
        lvl = f"[{str(level)}]".ljust(7)
        print(f"{self.timestamp()} {lvl} {message}")

    def show(
        self, level: str, color: Color, title: str, message: Optional[str]
    ) -> None:
        pprint(
            "\n".join(
                [
                    f"[{color}]{TOP_BAR}",
                    f"{MIDDLE_BAR} {level}:[/{color}] [bold]{title}[/bold]",
                ]
            )
        )
        if message:
            for line in message.split("\n"):
                pprint(f"[{color}]{MIDDLE_BAR} [/{color}] {line}")
        pprint(f"[{color}]{BOTTOM_BAR}[/{color}]")

    def trace(self, message: str) -> None:
        if self.is_level(Level.TRACE):
            self.log(Level.TRACE, message)

    def debug(self, message: str) -> None:
        if self.is_level(Level.DEBUG):
            self.log(Level.DEBUG, message)

    def info(self, message: str) -> None:
        if self.is_level(Level.INFO):
            self.log(Level.INFO, message)

    def warn(self, title: str, message: Optional[str] = None) -> None:
        if self.is_level(Level.WARN):
            self.show("Warn", "yellow", title, message)

    def error(self, title: str, message: Optional[str] = None) -> None:
        self.show("Error", "red", title, message)

    def exception(self, exc: Error) -> None:
        message: Optional[str] = None
        if exc.__doc__:
            message = textwrap.dedent(exc.__doc__)

        self.error(str(exc), message)

    def fatal(self, title: str, message: Optional[str] = None) -> NoReturn:
        self.error(title, message)
        raise Exit(1)

    def flagrant(self, text: str) -> None:
        banner = "FLAGRANT SYSTEM ERROR".center(79)
        pprint(f"[white on blue]{banner}[/white on blue]")
        pprint(f"[white on blue]{' ' * 79}[/white on blue]")
        for line in text.split("\n"):
            formatted = ("    " + line).ljust(79)
            inside = formatted[:79]
            outside = formatted[79:]
            pprint(f"[white on blue]{inside}[/white on blue]{outside}")
        pprint(f"[white on blue]{' ' * 79}[/white on blue]")

    def ok(self, message: str) -> None:
        pprint(f"[green]{message}[/green]")


class JSONLogger(Logger):
    # Higher precision - microseconds instead of milliseconds
    def timestamp(self) -> str:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    def log_json(self, level: Level, message: str) -> None:
        print(
            json.dumps(
                {
                    "@level": str(level).lower(),
                    "@message": message,
                    "@timestamp": self.timestamp(),
                }
            )
        )


logger: Logger = Logger(Level.WARN)


def configure_logger(env: Mapping[str, str] = os.environ) -> None:
    global logger

    if "TF_LOG" in env:
        if env["TF_LOG"] == Level.JSON:
            logger = JSONLogger(Level.JSON)
        elif not env["TF_LOG"]:
            pass
        else:
            logger.level = Level.from_str(env["TF_LOG"])


configure_logger()
