locals {
  banner  = <<EOT

#
# include: ${var.path}
#

EOT
  snippet = "${local.banner}${replace(var.snippet, "#!${var.interpreter}", "")}"
}
