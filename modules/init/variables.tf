variable "path" {
  description = "The path to the module.tfvars file"
  type        = number
  default     = null
}

variable "name" {
  description = "The name of your module"
  type        = string
}

variable "namespace" {
  description = "The namespace for your module"
  type        = string
}

variable "provider_" {
  description = "The main provider used by your module"
  type        = string
  default     = "aws"
}

variable "version_" {
  description = "The version of your module"
  type        = string
  default     = "1.0.0"
}

variable "description" {
  description = "A description for your module"
  type        = string
  default     = null
}

variable "module" {
  description = "The current module spec"
  type = object({
    name      = optional(string)
    namespace = optional(string)
    provider  = optional(string)
    version   = optional(string)
    private   = optional(bool)
    scripts   = optional(map(list(string)))
    # Deprecated.
    git = optional(object({
      main_branch = optional(string)
    }))
  })
  default = {}
}
