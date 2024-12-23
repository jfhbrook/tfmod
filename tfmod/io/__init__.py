from contextlib import contextmanager
import datetime
from enum import IntEnum
import json
import os
import textwrap
from typing import Generator, Literal, Mapping, Optional, Self

from rich import print as pprint

from tfmod.error import Error
from tfmod.interrupts import interrupt_received


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

    def show(self, level: str, color: Color, title: str, body: Optional[str]) -> None:
        pprint(
            "\n".join(
                [
                    f"[{color}]{TOP_BAR}",
                    f"{MIDDLE_BAR} {level}:[/{color}] [bold]{title}[/bold]",
                ]
            )
        )
        if body:
            pprint(f"[{color}]{MIDDLE_BAR}")
            for line in textwrap.dedent(body).strip().split("\n"):
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

    def panic(self, text: str) -> None:
        banner = "FLAGRANT SYSTEM ERROR".center(79)
        message = "TfMod experienced an unexpected, fatal error."
        bug_report = textwrap.dedent(
            """
            Consider filing an issue at:

                https://github.com/jfhbrook/tfmod/issues
            """
        )

        pprint(f"[white on blue]{banner}[/white on blue]")
        pprint(f"[white on blue]{' ' * 79}[/white on blue]")
        pprint(f"[white on blue]{message.ljust(79)}[/white on blue]")
        pprint(f"[white on blue]{' ' * 79}[/white on blue]")

        for line in text.split("\n")[1:-1]:
            formatted = ("    " + line).ljust(79)
            inside = formatted[:79]
            outside = formatted[79:]
            pprint(
                f"[white on blue]{inside}[/white on blue]" f"[white]{outside}[/white]"
            )

        for line in bug_report.split("\n"):
            pprint(f"[white on blue]{line.ljust(79)}[/white on blue]")

    def ok(self, message: str) -> None:
        pprint(f"[green]{message}[/green]")

    def hbar(self) -> None:
        try:
            columns, _ = os.get_terminal_size()
        except OSError:
            columns = 79
        pprint(f"[color(8)]{'─' * columns}[/color(8)]")

    def start_quote(self, message: str) -> None:
        pprint(f"[color(8)]{message}[/color(8)]")

    @contextmanager
    def wrap_quote(self) -> Generator[None, None, None]:
        self.hbar()

        yield

        self.hbar()

    @contextmanager
    def quote(self, message: str) -> Generator[None, None, None]:
        self.start_quote(message)
        with self.wrap_quote():
            yield


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


def prompt(
    name: str, message: str = "Enter a value:", description: Optional[str] = None
) -> Optional[str]:
    """
    A general prompt
    """

    pprint(f"[bold white]{name}[/bold white]")
    if description:
        pprint(f"[bold white]{textwrap.indent(description, " ")}[/bold white]")
    print("")

    # rich.Prompt doesn't have the right behavior.
    #
    # I'd use a formatter from rich, but it doesn't expose one. This is
    # probably because it goes through great pains to handle terminal width
    # appropriately, something a format method can't do.
    try:
        result = input(f"\u001b[1m{message}\u001b[0m ")
    except (KeyboardInterrupt, EOFError):
        print()
        interrupt_received()
        raise
    print("")
    return result


def prompt_confirm(question: str, description: str) -> bool:
    """
    Prompt to confirm y/N
    """

    result = prompt(question, "Enter a value:", description)

    if result in ["y", "Y", "yes", "YES"]:
        return True
    return False
