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

- [ ] tests
  - monkeypatch `run_*` commands
  - monkeypatch github API commands
  - snapshots for io
  - `bats` for bash, maybe a custom pytest runner
- [ ] publishing improvements
  - Fix docstrings - a lot of them are out of date
  - Workflow DSL
    - In particular, a `Dependency` abc with `may`, `must` and `validate`
      methods
    - Possibly a type for `Callable[[], List[Action]]`
    - There's a PR
  - `shlex` names
  - Detect if tag exists, only `--force` if necessary
  - Validate that provider is official/recognized
    - This seems to be a requirement to publish to Hashicorp
  - Validate directory name
  - Validate module structure
    - <https://developer.hashicorp.com/terraform/language/modules/develop/structure>
  - Validate on main branch
  - Validate github remote
  - Check if module is available through API
- [ ] flags
  - parse command flags automatically - no use case for "bleed-through"
  - `-force` publish flag
  - `-auto-approve` publish flag
- [ ] unwise/update bugs, etc
  - Somehow got in a state once where tfmod was empty except for state files
  - Command output quoting is fubar
  - Certain kinds of errors aren't behing appropriately handled
  - Command line parsing is Wrong
  - Write `doctor` command to help debug issues
- [ ] config
  - show `gh` config
  - show git config's `init.defaultBranch`
  - where to get preferred git remote type? ssh vs https?
  - may need to stop punting on bespoke config file
- [ ] script related commands
  - run
  - lint
  - fmt/format
  - test
  - validate
- [ ] viewing commands
  - docs - open terraform registry page in browser
  - namespace - open terraform registry page for namespace in browser
  - repo - open github repo in browser
  - unpublish - open appropriate page, with directions, in browser
- [ ] nice-to-haves
  - login
    - show `gh` status with directions to log in
    - open <https://registry.terraform.io/sign-in>
  - whoami - show `gh` user info
  - ping
    - github (public) API
    - terraform registry
- [ ] dist tagging (latest, beta etc)
  - TODO: how does npm implement dist-tag?
  - also implement npm's dist-tag behavior on publish
