locals {
  raw = file(var.path)
  snippet = replace(local.raw, "#!${interpreter}", "")
}
