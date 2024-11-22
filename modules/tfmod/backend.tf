terraform {
  required_version = ">= 1.7.2"

  required_providers {
    shell = {
      source  = "scottwinkler/shell"
      version = "~> 1.7.10"
    }
  }
}

provider "shell" {
  environment = {
    module_path = path.module
  }
  interpreter = ["/usr/bin/env", "python3", "-m", "tfmod.task"]
}
