import datetime
from enum import IntEnum
import json
import os
from typing import Literal, Mapping, Optional

from rich import print as pprint

from tfmod.error import Exit


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

    def __str__(self) -> str:
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

    def fatal(self, title: str, message: Optional[str] = None) -> None:
        self.error(title, message)
        raise Exit(1)

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
        elif env["TF_LOG"] not in Level:
            logger.level = Level.TRACE
        else:
            logger.level = Level[env["TF_LOG"]]


configure_logger()
