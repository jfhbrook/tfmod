locals {
  path = coalesce(var.path, "${path.cwd}/module.tfvars")
  content = provider::terraform::encode_tfvars({
    name        = var.name
    provider    = var.provider_
    version     = var.version_
    description = var.description

    scripts = {}
  })
}

resource "local_file" "module" {
  content  = local.content
  filename = local.path
}
