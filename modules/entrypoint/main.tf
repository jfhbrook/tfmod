locals {
  entrypoint = "${path.module}/../../tfmod/entrypoint.sh.tftpl"
  commands = [
    "",
    "version",
    "init",
    "config",
    "update",
    "unwise"
  ]
  snippets = {
    prelude    = "tfmod/prelude.sh"
    logging    = "tfmod/io/logging.sh"
    parse_args = "tfmod/command/parse-args.sh"
    update     = "tfmod/command/update.sh"
    unwise     = "tfmod/command/unwise.sh"
    main       = "tfmod/command/main.sh"
  }
}

module "snippet" {
  source   = "../shell-snippet"
  for_each = local.snippets
  snippet  = file("${path.module}/../../${each.value}")
  path     = "tfmod/${split("tfmod/", each.value)[1]}"
}

module "help" {
  source   = "../command-help"
  for_each = toset(local.commands)
  command  = each.key
}

resource "local_file" "entrypoint" {
  content = templatefile(local.entrypoint, {
    for name, mod in module.snippet : upper(name) => mod.snippet
  })
  filename = "${path.module}/../../bin/tfmod"
}