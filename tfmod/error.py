class Error(Exception):
    """
    TfMod experienced an error. This is likely a bug in TfMod. Consider filing
    an issue at:

        https://github.com/jfhbrook/tfmod/issues
    """


class Help(Error):
    pass


class Exit(Error):
    def __init__(self, exit_code: int) -> None:
        if exit_code:
            message = f"TfMod exited with an error (code: {exit_code})"
        else:
            message = "TfMod exited successfully"
        super().__init__(message)
        self.exit_code = exit_code


class CliError(Error):
    pass


class TerraformError(Error):
    """
    Terraform exited with an unsuccessful status. Ensure that the configuration
    is correct.
    """

    def __init__(self, exit_code: int) -> None:
        super().__init__(f"Terraform experienced an error (code: {exit_code})")
        self.exit_code: int = exit_code
