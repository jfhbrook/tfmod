variable "path" {
  description = "The path to your module's module.tfvars"
  type        = string
  default     = null
}

variable "name" {
  description = "The name of your module"
  type        = string
}

variable "module_provider" {
  description = "The main provider used by your module"
  type        = string
}

variable "module_version" {
  description = "The version of your module"
  type        = string
}

variable "description" {
  description = "A description for your module"
  type        = string
}

variable "module" {
  description = "The module spec"
  type        = map(any)
  default     = null
}
