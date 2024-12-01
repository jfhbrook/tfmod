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
  - [ ] Workflow DSL
    - In particular, a `Dependency` abc with `may`, `must` and `validate`
      methods
    - Possibly a type for `Callable[[], List[Action]]`
  - [ ] validate that provider is official/recognized
  - [ ] validate directory name
  - [ ] validate module structure
    - <https://developer.hashicorp.com/terraform/language/modules/develop/structure>
  - [ ] validate on main branch
  - [ ] validate github remote
  - [ ] open publish page (if module not available)
  - [ ] check if module is available through API
  - [ ] `-force` flag
- [ ] unwise/update bug involving malformed directory
  - I somehow to got things in a state where tfmod was empty except for
    state files
  - that predictably broke a ton of stuff
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
- [ ] HOLD: weird help parsing error
  - it showed up and later magically went away. is this recurring?
- [ ] what now?


## resources

- [publishing a public module](https://developer.hashicorp.com/terraform/registry/modules/publish)
- [standard module structure](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [terraform registry http api](https://developer.hashicorp.com/terraform/registry/api-docs)
  - it looks like it doesn't support creating/publishing a module, might need
    to get creative
  - potentially worth writing a Python client library for it anyway, though?
- [PyGithub](https://github.com/PyGithub/PyGithub)
  - can set the repository description
  - can potentially create the repository if it doesn't exist
- [pygit2](https://github.com/libgit2/pygit2)
  - or just shell out to git lol
- [python-hcl2](https://pypi.org/project/python-hcl2/)
- [go-flag](https://github.com/jfhbrook/go-flag)
  - doesn't have particular support for positional args. I'm not sure how
    terraform solves that - terraform *does* use the flag package, as far as
    I know
