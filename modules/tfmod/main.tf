resource "shell_script" "lint" {
  count = var.command == "lint" ? 1 : 0
  lifecycle_commands {
    read   = "lint -read"
    create = "lint -create"
    update = "lint -update"
    delete = "lint -destroy"
  }

  environment = {
  }

  working_directory = path.cwd
}
