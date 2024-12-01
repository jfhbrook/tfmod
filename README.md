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

- [ ] publishing improvements
  - Check if module is available through API
- [ ] flags
  - parse command flags automatically - no use case for "bleed-through"
  - `-force` publish flag
  - `-auto-approve` publish flag
- [ ] bash (unwise/update) bugs and tests
  - Somehow got in a state once where tfmod was empty except for state files
  - Command output quoting is fubar
  - Certain kinds of errors aren't behing appropriately handled
  - Command line parsing is Wrong
  - Write `doctor` command to help debug issues
  - `bats`, maybe a custom pytest runner
- [ ] check for updates in version command
- [ ] python bugs and tests
  - monkeypatch `run_*` commands
  - monkeypatch github API commands
  - snapshots for io
  - Bug: Attempts to update description to None if empty in module.tfvars
    - Shouldn't spec validation catch this?
    - Shouldn't init default it to something?
  - Question: Is namespace actually required? Isn't that implied by GitHub?
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
- [ ] more publishing improvements
  - dist tagging (latest, beta, etc)
    - TODO: how does npm implement dist-tag?
    - NOTE: `npm` has a separate companion command too
  - Detect if tag exists, only `--force` if necessary
