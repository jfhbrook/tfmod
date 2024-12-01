import os
from typing import Any, cast

from tfmod.error import GitDirtyError, GitRepoNotFoundError, SpecNotFoundError
from tfmod.gh import gh_client
from tfmod.git import GitRepo
from tfmod.io import prompt_actions
from tfmod.spec import Spec
from tfmod.terraform import Terraform
from tfmod.version import Version


def validate_spec() -> None:
    cmd = Terraform("spec").isolated_state().spec().auto_approve()
    cmd.run()


def load_spec() -> Spec:
    try:
        spec = Spec.load()
    except FileNotFoundError:
        raise SpecNotFoundError("No module.tfvars found")

    return spec


def load_git() -> GitRepo:
    try:
        repo = GitRepo.load()
    except GitRepoNotFoundError:
        if prompt_actions([("+", "git init")]):
            repo = GitRepo.init()
        else:
            raise

    # TODO: Validate that the current branch is the main branch. Needs some
    # reliable-ish way to detect what the main branch is. This will either be
    # through configuration (in module.tfvars or in main config) or detected
    # via something like:
    #
    #     https://stackoverflow.com/questions/28666357/how-to-get-default-git-branch

    # TODO: -force flag
    if repo.dirty():
        if prompt_actions([("~", "git add ."), ("~", "git commit")]):
            repo.add(".")
            repo.commit()
        else:
            raise GitDirtyError("All files must be committed to continue.")

    if repo.dirty():
        raise GitDirtyError("All files must be committed to continue.")

    return repo


def load_github(spec: Spec, git: GitRepo) -> None:
    name = spec.repo_name()
    client = gh_client()
    # TODO: Pull/parse git remotes from GitRepo
    # TODO if a git remote for github
    # - parse/save remote name
    # - parse repo
    # TODO if github repo does not exist
    # - shell into `gh` to create it
    # - add as remote
    # TODO: check/update description based on module.tfvars

    # required return values:
    # - github repo namespace
    # - github repo name
    pass


def update_description(description: str) -> None:
    raise NotImplementedError("update_description()")


def validate_git(path: str, spec: Spec, git: GitRepo, github: Any) -> None:
    # spec vs directory name
    # spec vs github repo name
    # spec vs git remote url
    raise NotImplementedError("validate_git()")


def validate_module() -> None:
    raise NotImplementedError("validate_module()")


def tag_and_push(version: Version) -> None:
    raise NotImplementedError("tag_and_push")


def is_package_available() -> bool:
    return False


def open_package_url() -> None:
    raise NotImplementedError("open_package_url")


def publish() -> None:
    validate_spec()

    spec = load_spec()
    version = Version.parse(cast(str, spec.version))
    description = cast(str, spec.description)

    git = load_git()
    github: Any = load_github(spec, git)

    if description != github.description:
        update_description(description)

    validate_git(path=os.getcwd(), spec=spec, git=git, github=github)

    validate_module()

    tag_and_push(version)

    if not is_package_available():
        open_package_url()
