from dataclasses import dataclass
import functools
import sys
import textwrap
from typing import Callable, Dict, NoReturn, Optional

import flag

from tfmod.error import Error


@dataclass
class Command:
    """
    A command
    """

    name: str
    help: str
    command: "Callable[[Command], None]"

    def run(self) -> None:
        self.command(self)


CommandRunner = Callable[[Command], None]

COMMANDS: Dict[str, Command] = dict()


def command(
    name: Optional[str] = None, help: Optional[str] = None
) -> Callable[[CommandRunner], CommandRunner]:
    """
    Define a command
    """

    def decorator(command: CommandRunner) -> CommandRunner:
        command_name: str = name if name else command.__name__
        help_message: str = "???"

        if help:
            help_message = help
        elif command.__doc__:
            help_message = textwrap.dedent(command.__doc__).strip()
        cmd = Command(name=command_name, help=help_message, command=command)
        COMMANDS[command_name] = cmd
        return command

    return decorator


@flag.usage
def usage():
    """
    Show command usage
    """

    if len(flag.args):
        command = flag.args[0]

        if command in COMMANDS:
            print(f"usage: tfmod [OPTIONS] {command}")
            print("")
            print(COMMANDS[command].help)
            return

    print("Usage: tfmod [OPTIONS] [COMMAND]")
    print("")
    print("Commands:")
    print("")

    for command in COMMANDS.values():
        print(f"	{command.name}    {command.help}")

    print("")


class Help(Error):
    """
    Signals help
    """


def help() -> NoReturn:
    """
    Show usage and exit
    """
    raise Help()


class Exit(Error):
    """
    Signals an exit
    """

    def __init__(self, exit_code: int) -> None:
        super().__init__(f"Exit({exit_code}")
        self.exit_code = exit_code


def exit(exit_code: int = 0) -> NoReturn:
    """
    Exit with a status code (default: 0)
    """
    raise Exit(exit_code)


class CliError(Error):
    """
    An exception for CLI errors
    """


def error(message: str) -> NoReturn:
    """
    Print a CLI error message, show usage, and exit(2)
    """
    raise CliError(message)


def not_found() -> NoReturn:
    """
    Command not found
    """

    error(f"Unknown command {command}")


def none_specified() -> NoReturn:
    """
    No command was specified
    """
    error("No command specified")


Main = Callable[[], None]


def cli(fn: Main) -> Main:
    """
    Handle CLI errors
    """

    @functools.wraps(fn)
    def cli() -> None:
        try:
            fn()
        except Help:
            usage()
            sys.exit(0)
        except Exit as exc:
            sys.exit(exc.exit_code)
        except CliError as exc:
            print(f"error: {exc}")
            print("")
            usage()
            sys.exit(2)

    return cli


def run() -> None:
    """
    Run any specified command
    """
    command: Optional[str] = None

    if len(flag.args):
        command = flag.args[0]

    if not command:
        none_specified()

    if command == "help":
        flag.args.pop(0)
        help()

    if command in COMMANDS:
        cmd = COMMANDS[command]
        flag.args.pop(0)
        cmd.run()

        exit()
    else:
        not_found()
