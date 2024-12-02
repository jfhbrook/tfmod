from typing import Self


class Error(Exception):
    """
    TfMod experienced an error. This is likely a bug in TfMod. Consider filing
    an issue at:

        https://github.com/jfhbrook/tfmod/issues
    """


class Help(Error):
    pass


class Exit(Error):
    def __init__(self: Self, exit_code: int) -> None:
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
    Terraform exited unsuccessfully. Ensure that the configuration is correct.
    """

    def __init__(self, exit_code: int) -> None:
        super().__init__(f"Terraform experienced an error (code: {exit_code})")
        self.exit_code: int = exit_code


class SpecValueError(Error):
    """
    The contents of the module.tfvars file are invalid for this operation. Ensure your
    module.tfvars file is complete and try again.
    """


class SpecNotFoundError(Error):
    """
    TfMod requires a module.tfvars file to continue. You can initialize a module.tfvars
    file by running "tfmod init".
    """


class GitError(Error):
    """
    TfMod encountered an error when trying to use git. Consider filing an issue at:

        https://github.com/jfhbrook/tfmod/issues
    """

    def __init__(self: Self, message: str, stderr: bytes) -> None:
        super().__init__(message)
        self.stderr = stderr


class GitRepoNotFoundError(GitError):
    """
    TfMod could not find a git repository at this location. To initialize a git
    repository, run "git init".
    """


class GitHeadNotFoundError(GitError):
    """
    The git repository has no commits. Try running:

        git add .
        git commit -m 'First commit'
    """


class GhError(Error):
    """
    TfMod encountered an error when trying to use the gh CLI. Check your configuration
    and try again.
    """


class PublishError(Error):
    """
    TfMod encountered an error when trying to publish your module.
    """


class GhRemoteNotFoundError(PublishError):
    """
    TfMod was unable to find a GitHub remote for this repository. Make sure
    that a git remote is defined that is hosted by GitHub.
    """


class DefaultBranchError(PublishError):
    """
    TfMod detected that the current branch is not the default and will not
    continue. To override this behavior, set the -force flag.
    """


class GitDirtyError(PublishError):
    """
    TfMod detected uncommitted changes in the current project and will not
    continue. To override this behavior, set the -force flag.
    """


class PlanError(Error):
    """
    TfMod encountered an error while creating the plan.
    """


class ApplyError(PlanError):
    """
    TfMod encountered an error while applying the plan.
    """


class ApplyInterruptError(ApplyError):
    """
    TfMod was interrupted while applying the plan.
    """


class ResourceError(PlanError):
    """
    An exception occurred while resolving a resource.
    """
