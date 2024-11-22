locals {
  path = coalesce(var.path, "${path.cwd}/module.tfvars")
}
