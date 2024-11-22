import flag

from tfmod.cli.base import command, Command, parse


@command()
def init(cmd: Command) -> None:
    """
    initialize a new project
    """

    print(cmd)
    print(flag.args)


def main() -> None:
    parse()
