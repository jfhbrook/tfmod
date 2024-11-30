locals {
  raw = var.snippet
  snippet = replace(local.raw, "#!${interpreter}", "")
}
