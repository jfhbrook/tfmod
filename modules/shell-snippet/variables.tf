variable "path" {
  description = "The path to a shell script source"
  type        = string
}

variable "interpreter" {
  description = "The interpreter, as seen in a shebang"
  type        = string
  default     = "/usr/bin/env bash"
