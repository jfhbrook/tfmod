locals {
  raw     = var.snippet
  snippet = replace(local.raw, "#!${var.interpreter}", "")
}
