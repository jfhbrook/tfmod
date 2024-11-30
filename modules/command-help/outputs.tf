output "help" {
  description = "The command's help text"
  value       = data.shell_script.help.output["help"]
}
