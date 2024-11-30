data "shell_script" "help" {
  lifecycle_commands {
    read = file("${path.module}/help.sh")
  }

  environment = {
    command = var.command != null ? var.command : ""
  }

  interpreter = ["/usr/bin/env", "bash", "-c"]
}
