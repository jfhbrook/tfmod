# tfmod

Publish Terraform modules to GitHub, following
[Hashicorp's documented practices](https://developer.hashicorp.com/terraform/registry/modules/publish).

## How Ready is This?

**It works on my machine!**

But for real - it's currently pretty limited, is missing a lot of features,
and doesn't have tests. I also don't currently have any modules that I can
publish to the public registry, as I tend to use off-label providers.

That said, it's useful to me today. I use it to tag my `terraform-shell-git-*`
modules, with moderate success. I suspect that it will cowpath over time.

## Usage

### Installing and Updating

To install, download and run the install script:

```sh
curl -LsSf https://raw.githubusercontent.com/jfhbrook/tfmod/refs/heads/main/install.sh 
```

To update once it's installed:

```sh
tfmod update
```

That should all work, theoretically. The install/update script needs a little love.

### Setting Up a Terraform Module

To get started, run:

```sh
tfmod init
```

This will create a file called `module.tfvars` which contains all the
configuration tfmod (currently) needs to publish packages.

### Publishing

We have lazers!!!

```sh
tfmod publish
```

That will generate a list of actions to execute in order to publish the
module:

![](https://github.com/jfhbrook/tfmod/blob/main/img/publish.jpg?raw=true)

## Development

There's a `justfile` that's reasonably well-documented. I currently don't
have tests, but get a lot of mileage out of `just check` and `just lint`.

## License

MIT. See the LICENSE file for more details.

## TODOs

Hoo boy...

- [ ] write tests
  - do them for bash too
- [ ] Publish part 2 (pushing back because part 1 is way too big and I need
      a sensible milestone)
  - [ ] Fix docstrings - a lot of them are out of date
  - [ ] Workflow DSL
    - In particular, a `Dependency` abc with `may`, `must` and `validate`
      methods
    - Possibly a type for `Callable[[], List[Action]]`
  - [ ] validate that provider is official/recognized
    - This seems to be a requirement to publish to Hashicorp
  - [ ] validate directory name
  - [ ] validate module structure
    - <https://developer.hashicorp.com/terraform/language/modules/develop/structure>
  - [ ] validate on main branch
  - [ ] validate github remote
  - [ ] check if module is available through API
  - [ ] `-force` flag
  - [ ] `-auto-approve` flag
- [ ] unwise/update bugs
  - Somehow got in a state once where tfmod was empty except for state files
- [ ] config
  - needs so far kinda sorted by `gh` config and/or `git` config
    - git prefer https or ssh
    - git prefer main branch
  - but can at least show the `gh` config, yeah?
- [ ] fix command output quoting (both python and bash)
- [ ] login
  - log github cli login status
  - open <https://registry.terraform.io/sign-in>
- [ ] whoami
  - github whoami mostly
- [ ] viewing commands
  - [ ] docs - open terraform registry page in browser
  - [ ] namespace - open terraform registry page for namespace in browser
  - [ ] repo - open github repo in browser
  - [ ] unpublish - open appropriate page, with directions, in browser
- [ ] ping
  - github
  - terraform registry
- [ ] script related commands
  - [ ] run
  - [ ] lint
  - [ ] fmt/format
  - [ ] test
  - [ ] validate
- [ ] doctor
  - "is installed correctly", for now
- [ ] tagging (latest, beta etc)
  - TODO: how does npm implement dist-tag?
  - also implement npm's dist-tag behavior on publish
