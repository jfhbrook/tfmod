variable "command" {
  description = "The tfmod command to run"
  type        = string
  default     = null
}

variable "module" {
  description = "The module spec"
  type        = map(any)
}
