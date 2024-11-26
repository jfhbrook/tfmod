import os.path

from tfmod.constants import CONFIG_DIR, CONFIG_TFVARS

TEMPLATE = """
"""


# TODO: Should I use Terraform itself to create the config file?
# https://developer.hashicorp.com/terraform/language/functions/terraform-encode_tfvars
def init_config() -> None:
    if not os.path.isfile(CONFIG_TFVARS):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_TFVARS, "w") as f:
            f.write(TEMPLATE)
