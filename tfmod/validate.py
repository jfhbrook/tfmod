import fnmatch
import os
from pathlib import Path
import re
import textwrap
from typing import Generator, Iterable, List, Self

from tfmod.io import logger

"""
Functions to validate the structure and contents of a given module.
"""

#
# Checks involving misplaced Terraform files. This is untested and has a
# really high danger of becoming a performance nightmare if done wrong, so
# is currently inert - but waiting for when I can write tests.
#


class GitIgnore:
    """
    A loaded .gitignore with the ability to find matched files
    """

    def __init__(self: Self, path: str) -> None:
        ignore: List[str] = list()

        # We at least make an *attempt* to respect .gitignore. This is hard to
        # fully test, but if the validation step is super slow, this being
        # broken is why.
        try:
            with open(Path(path) / ".gitignore", "r") as f:
                for line in f:
                    if re.match(r"^\s*#", line):
                        continue
                    ignore.append(line)
        except FileNotFoundError as exc:
            logger.debug(str(exc))

        self.ignore = ignore

    def matching(self: Self, files: Iterable[str]) -> Generator[str, None, None]:
        for pat in self.ignore:
            for f in fnmatch.filter(files, pat):
                yield f


def misplaced_terraform_files(path: str) -> List[str]:
    """
    Find Terraform files that are "misplaced" - that is, not in the project
    root nor in a subdirectory of ./modules
    """
    misplaced: List[str] = list()
    ignore = GitIgnore(path)

    for root, dirs, files in os.walk(path):
        if root == path:
            # imo, .tf files in ./test(s) is OK
            for test_dir in ["test", "tests"]:
                if test_dir in dirs:
                    dirs.remove(test_dir)
            # Terraform files in the root are fine
            continue

        # Files under path/modules/X are OK, but files under path/modules/X/Y
        # are not. We still have to traverse the child paths, but we don't
        # have to check the files.
        if Path(root).parent == Path(path) / "modules":
            continue

        # Don't iterate over directories matching the gitignore, don't test
        # files matching the gitignore
        for entities in [files, dirs]:
            for e in ignore.matching([str(Path(root) / e) for e in entities]):
                entities.remove(e)

        for file in files:
            if file.endswith(".tf"):
                misplaced.append(file)

    return misplaced


def validate_terraform_files(path: str) -> None:
    """
    Validate that all Terraform files are in their expected locations - that
    is, either in the project root or under the ./modules folder. If violations
    are found, show warnings.
    """
    misplaced = misplaced_terraform_files(path)

    if misplaced:
        title = "Module has Terraform files in unapproved locations"
        body = "The following files are in unapproved locations:\n\n"
        for file in misplaced:
            body += f"- {file}\n"
        body += textwrap.dedent(
            """
            Terraform files must either be in the project root or inside modules in the
            ./modules folder. For more information, see:

                https://developer.hashicorp.com/terraform/language/modules/develop/structure
            """
        )

        logger.warn(title, body)


#
# This validation, on the other hand, is good to go
#


def validate_readme(path: str) -> None:
    """
    Validate that the project has a README.md. Terraform Registry uses this
    to populate their documentation pages.
    """
    if not os.path.isfile(Path(path) / "README.md"):
        logger.warn(
            title="No README.md found",
            message="""
            The Terraform expects a README.md in the root of your
            project, and uses it to generate documentation on their site. For
            more information, see:

                https://developer.hashicorp.com/terraform/registry/modules/publish
            """,
        )
