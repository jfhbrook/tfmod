variable "module" {
  description = "The module spec"
  type = object({
    name      = string
    namespace = string
    provider  = string
    version   = string
    private   = optional(bool)
    scripts   = optional(map(list(string)))
    git = optional(object({
      main_branch = optional(string)
    }))
  })
  validation {
    condition     = len(regexall("\\d+\\.\\d+\\.\\d+", "1.2.3")) > 0
    error_message = "The version must follow simplified semver (ie. 1.2.3)"
  }
}
