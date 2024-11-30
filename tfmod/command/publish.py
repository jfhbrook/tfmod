from typing import Any

from tfmod.error import GitDirtyError, GitRepoNotFoundError, SpecNotFoundError
from tfmod.git import git_add, git_commit, git_init, git_is_dirty, GitRepo
from tfmod.io import logger, prompt_confirm
from tfmod.spec import parse_version, Spec
from tfmod.terraform import Terraform


def validate_spec() -> None:
    cmd = Terraform("spec", "plan").spec()
    cmd.run()


def load_spec() -> Spec:
    try:
        spec = Spec.load()
    except FileNotFoundError:
        raise SpecNotFoundError("No module.tfvars found")

    version = parse_version(spec)

    return spec


def load_git() -> GitRepo:
    try:
        repo = GitRepo.load()
    except GitRepoNotFoundError:
        if prompt_confirm("Would you like to initialize a git repo?"):
            git_init()
            repo = GitRepo.load()
        else:
            raise

    # TODO: Validate that the current branch is the main branch. Needs some
    # reliable-ish way to detect what the main branch is. This will either be
    # through configuration (in module.tfvars or in main config) or detected
    # via something like:
    #
    #     https://stackoverflow.com/questions/28666357/how-to-get-default-git-branch

    # TODO: -allow-dirty flag
    if git_is_dirty():
        if prompt_confirm("Would you like to add and commit changes?"):
            git_add(".")
            git_commit("Committed by TfMod")
        else:
            raise GitDirtyError("All files must be committed to continue.")

    if git_is_dirty():
        raise GitDirtyError("All files must be committed to continue.")

    return repo


def load_github() -> None:
    # TODO construct repo name from module.tfvars
    # - warn if directory name does not match what's in module.tfvars
    # TODO if a git remote for github
    # - parse/save remote name
    # - parse repo
    # TODO if github repo does not exist
    # - shell into `gh` to create it
    # - add as remote
    # TODO: check/update description based on module.tfvars

    pass


def update_description(description: str) -> None:
    raise NotImplementedError("update_description()")


def validate_git(spec: Spec, git: GitRepo, github: Any) -> None:
    raise NotImplementedError("validate_git()")


def validate_module() -> None:
    raise NotImplementedError("validate_module()")


def tag_and_push() -> None:
    raise NotImplementedError("tag_and_push")


def is_package_available() -> bool:
    return False


def open_package_url() -> None:
    raise NotImplementedError("open_package_url")


def publish() -> None:
    validate_spec()

    spec = load_spec()
    git = load_git()
    github: Any = load_github()

    if not spec.description:
        logger.warn("No description specified for spec")
    elif spec.description != github.description:
        update_description(spec.description)

    validate_git(spec, git, github)
    validate_module()

    tag_and_push()

    if not is_package_available():
        open_package_url()
