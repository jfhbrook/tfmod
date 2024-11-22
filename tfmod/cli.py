from dataclasses import dataclass
import sys
from typing import Dict, List, NoReturn, Optional

import flag


@dataclass
class Command:
    name: str
    help: str

    def run(self) -> None:
        print("init")
        print(flag.args)


commands: Dict[str, Command] = dict(
    init=Command(name="init", help="initialize a new project")
)


@flag.usage
def usage():
    if len(flag.args):
        command = flag.args[0]

        if command in commands:
            print(f"usage: tfmod [OPTIONS] {command}")
            print("")
            print(commands[command].help)
            return

    print("usage: tfmod [OPTIONS] [COMMAND]")
    print("")
    print("COMMANDS")
    print("")

    for command in commands.values():
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


def main() -> None:
    flag.parse()
    command: Optional[str] = None
    
    if len(flag.args):
        command = flag.args[0]

    if not command:
        bail("no command specified")

    if command == "help":
        flag.args.pop(0)
        help()

    if command in commands:
        cmd = commands[command]
        flag.args.pop(0)
        cmd.run()
    else:
        bail(f"unknown command {command}")
