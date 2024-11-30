locals {
  entrypoint = "${path.module}/../../tfmod/entrypoint.sh.tftpl"
  parse_args = "${path.module}/../../tfmod/command/parse-args.sh.tftpl"
  commands = [
    "",
    "update",
    "unwise"
  ]
  snippets = {
    prelude = "tfmod/prelude.sh"
    logging = "tfmod/io/logging.sh"
    prompt  = "tfmod/io/prompt.sh"
    update  = "tfmod/command/update.sh"
    unwise  = "tfmod/command/unwise.sh"
    main    = "tfmod/command/main.sh"
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

locals {
  template_snippets = {
    for name, mod in module.snippet : upper(name) => mod.snippet
  }
  template_partials = {
    PARSE_ARGS = templatefile(local.parse_args, {
      for name, mod in module.help : "HELP_${name == "" ? "MAIN" : upper(name)}" => mod.help
    })
  }
  template_vars = merge(local.template_snippets, local.template_partials)
}

resource "local_file" "entrypoint" {
  content  = templatefile(local.entrypoint, local.template_vars)
  filename = "${path.module}/../../bin/tfmod"
}
