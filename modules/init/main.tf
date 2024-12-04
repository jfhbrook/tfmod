locals {
  path    = coalesce(var.path, "${path.cwd}/module.tfvars")
  scripts = var.module.scripts == null ? {} : var.module.scripts
  content = provider::terraform::encode_tfvars({
    module = {
      name        = var.name
      provider    = var.provider_
      namespace   = var.namespace
      version     = var.version_
      description = var.description
      private     = var.module == null ? false : coalesce(var.module.private, false)

      scripts = local.scripts
    }
  })
}

resource "local_file" "module" {
  content  = local.content
  filename = local.path
}
