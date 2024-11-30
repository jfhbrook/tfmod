variable "snippet" {
  description = "A shippet of shell script source"
  type        = string
}

variable "path" {
  description = "The path to the shell script source"
  type        = string
  default     = "<unspecified>"
}

variable "interpreter" {
  description = "The interpreter, as seen in a shebang"
  type        = string
  default     = "/usr/bin/env bash"
}
