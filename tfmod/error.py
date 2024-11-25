class Error(Exception):
    """
    A TfMod base error.
    """


class Help(Error):
    """
    Signals help
    """


class Exit(Error):
    """
    Signals an exit
    """

    def __init__(self, exit_code: int) -> None:
        super().__init__(f"Exit({exit_code}")
        self.exit_code = exit_code


class CliError(Error):
    """
    A command line error
    """
