locals {
  path       = "${path.module}/../../tfmod/entrypoint.sh.tftpl"
  entrypoint = templatefile(local.path, {})
}

resource "local_file" "entrypoint" {
  content  = local.entrypoint
  filename = "${path.module}/../../bin/tfmod"
}
