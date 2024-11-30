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
}
