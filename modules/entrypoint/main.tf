locals {
  entrypoint = "${path.module}/../../tfmod/entrypoint.sh.tftpl"
  prelude    = file("${path.module}/../../tfmod/io/prelude.sh")
  logging    = file("${path.module}/../../tfmod/io/logging.sh")
}

resource "local_file" "entrypoint" {
  content = templatefile(local.entrypoint, {
    PRELUDE = local.prelude
    LOGGING = local.logging
  })
  filename = "${path.module}/../../bin/tfmod"
}
