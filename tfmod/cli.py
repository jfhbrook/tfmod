from dataclasses import dataclass
import sys
from typing import Dict, List, Optional

import flag


@dataclass
class Command:
    name: str
    help: str


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

    print(
        """usage: tfmod [OPTIONS] [COMMAND]

COMMANDS
"""
    )

    for command in commands.values():
        print(f"	{command.name}    {command.help}")

    print("")


def main() -> None:
    flag.parse()
    command: Optional[str] = flag.args[0] if len(flag.args) else None
    args: List[str] = flag.args[1:]

    if not command:
        usage()
        sys.exit(2)

    if command == "help":
        flag.args.pop(0)
        usage()
        sys.exit(0)

    if command in commands:
        cmd = commands[command]
    else:
        print(f"error: unknown command {command}")
        usage()
        sys.exit(2)

    print(cmd)
    print(args)
