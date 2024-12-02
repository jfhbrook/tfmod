from typing import Optional, Self

from tfmod.io import logger
from tfmod.plan import Resource
from tfmod.spec import Spec
from tfmod.terraform import Terraform

# The Terraform Registry seems to only allow modules to be published which
# use recognized providers. That surely includes official providers. It
# *may* also include partner providers, though listing those manually is a
# much bigger chore.
OFFICIAL_PROVIDERS = {
    "aws",
    "azurerm",
    "google",
    "kubernetes",
    "alicloud",
    "oracle",
    "ad",
    "archive",
    "assert",
    "awscc",
    "azuread",
    "azurestack",
    "boundary",
    "cloudinit",
    "consul",
    "dns",
    "external",
    "google-beta",
    "googleworkspace",
    "hcp",
    "hcs",
    "helm",
    "http",
    "local",
    "nomad",
    "null",
    "opc",
    "oraclepaas",
    "random",
    "salesforce",
    "template",
    "tfe",
    "tfmigrate",
    "time",
    "tls",
    "vault",
    "vsphere",
}


class SpecResource(Resource[Spec]):
    def get(self: Self) -> Optional[Spec]:
        # We validate with Terraform before trying to load. This is because
        # we want to see Terraform errors prior to choking on the load.
        self._pre_validate()
        return Spec.load()

    def _pre_validate(self: Self) -> None:
        cmd = Terraform("spec").isolated_state().spec().auto_approve()
        cmd.run()

    def validate(self, resource: Spec) -> None:
        # This SHOULD get handled during Terraform validation.
        assert resource.provider

        if resource.provider not in OFFICIAL_PROVIDERS and not resource.private:
            logger.warn(
                title=f"${resource.provider} is not an official provider",
                message="""If the Terraform Registry does not recognize the
                provider, it may not allow you to publish it.

                To quiet this message, set the "private" field in your
                module.tfvars file.
                """,
            )
