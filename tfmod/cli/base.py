from dataclasses import dataclass
import sys
import textwrap
from typing import Callable, Dict, NoReturn, Optional

import flag


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


def help() -> NoReturn:
    """
    Print usage and exit cleanly
    """
    usage()
    sys.exit(0)


def bail(message: str) -> NoReturn:
    """
    Print an error, print usage and exit 2
    """
    print(f"error: {message}")
    print("")
    usage()
    sys.exit(2)


def parse() -> None:
    flag.parse()
    command: Optional[str] = None

    if len(flag.args):
        command = flag.args[0]

    if not command:
        bail("no command specified")

    if command == "help":
        flag.args.pop(0)
        help()

    if command in COMMANDS:
        cmd = COMMANDS[command]
        flag.args.pop(0)
        cmd.run()
    else:
        bail(f"unknown command {command}")
