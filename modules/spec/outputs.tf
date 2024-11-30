output "name" {
  description = "The name of the module"
  value       = var.module.name
}

output "namespace" {
  description = "The namespace of the module"
  value       = var.module.namespace
}

output "provider" {
  description = "The provider of the module"
  value       = var.module.provider
}

output "version" {
  description = "The version of the module"
  value       = var.module.version
}

output "private" {
  description = "Whether or not the module is private"
  value       = coalesce(var.module.private, false)
}
