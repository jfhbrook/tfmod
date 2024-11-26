variable "path" {
  description = "The path to the module.tfvars file"
  type        = number
  default     = null
}

variable "name" {
  description = "The name of your module"
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
  default     = 3
}
