locals {
  entrypoint = "${path.module}/../../tfmod/entrypoint.sh.tftpl"
  prelude    = file("${path.module}/../../tfmod/io/prelude.sh")
  logging    = file("${path.module}/../../tfmod/io/logging.sh")
  parse_args = file("${path.module}/../../tfmod/command/parse-args.sh")
}

resource "local_file" "entrypoint" {
  content = templatefile(local.entrypoint, {
    PRELUDE    = local.prelude
    LOGGING    = local.logging
    PARSE_ARGS = local.parse_args
  })
  filename = "${path.module}/../../bin/tfmod"
}
