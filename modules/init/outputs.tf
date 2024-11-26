output "path" {
  description = "The path to your module.tfvars"
  value       = local.path
}

output "content" {
  description = "The content written to your module.tfvars"
  value       = local.content
}
