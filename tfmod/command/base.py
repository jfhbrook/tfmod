from dataclasses import dataclass
import functools
import sys
import textwrap
import traceback
from typing import Callable, Dict, List, NoReturn, Optional

import flag

from tfmod.error import CliError, Error, Exit, Help, TerraformError
from tfmod.io import logger

CommandRunner = Callable[[], None]


@dataclass
class Command:
    """
    A command
    """

    name: str
    help: str
    command: CommandRunner

    def run(self) -> None:
        self.command()


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


def print_global_defaults() -> None:
    """
    Print global default flags
    """

    def visitor(fl: flag.Flag) -> None:
        # TODO: Configure with flag method wrapper
        value_name: Optional[str] = None

        if fl.def_value != "false":
            value_name = "VALUE"

        # TODO: Wrap usage at 79 chars
        print(
            f"  -{fl.name}"
            + ("=" + value_name if value_name is not None else "")
            + fl.usage
        )
        b: List[str] = []
        b += f"  -{fl.name}"

    flag.visit_all(visitor)


@flag.usage
def usage():
    """
    Show command usage
    """

    if len(flag.args):
        command = flag.args[0]

        if command in COMMANDS:
            print(f"Usage: tfmod [OPTIONS] {command}")
            print("")
            print(COMMANDS[command].help)
            return

    print("Usage: tfmod [OPTIONS] [COMMAND]")
    print("")
    print("Commands:")

    for command in COMMANDS.values():
        print(f"  {command.name}          {command.help}")

    print("")

    print("Global options (use these before the subcommand, if any):")

    print_global_defaults()

    print("")


def help() -> NoReturn:
    """
    Show usage and exit
    """
    raise Help()


def exit(exit_code: int = 0) -> NoReturn:
    """
    Exit with a status code (default: 0)
    """
    raise Exit(exit_code)


def error(message: str) -> NoReturn:
    """
    Print a CLI error message, show usage, and exit(2)
    """
    raise CliError(message)


def not_found(command: str) -> NoReturn:
    """
    Command not found
    """

    error(
        f"""TfMod has no command named "{command}".

To see all of TfMod's top-level commands, run:
  terraform -help"""
    )


def none_specified() -> NoReturn:
    """
    No command was specified
    """
    help()


Main = Callable[[], None]


def cli(fn: Main) -> Main:
    """
    Handle CLI errors
    """

    flag.command_line.output = sys.stdout

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
            print(str(exc))
            sys.exit(2)
        except TerraformError as exc:
            # In theory, Terraform should report its own errors
            logger.debug(traceback.format_exc())
            sys.exit(1)
        except Error as exc:
            logger.exception(exc)
            sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            pass
        except Exception:
            logger.panic(traceback.format_exc())
            sys.exit(1)

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
        not_found(command)
