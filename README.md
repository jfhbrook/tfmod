# tfmod

## TODOs

- [ ] publish
  - [ ] identify less happy paths, stub tests
    - A lot of them are uncommon, oops
- [ ] tests
  - do after publish is working, since that's the main functionality and the
    APIs should have solidified by then
  - do them for bash too
- [ ] Publish part 2 (pushing back because part 1 is way too big and I need
      a sensible milestone)
  - [ ] Workflow DSL
    - In particular, a `Dependency` abc with `may`, `must` and `validate`
      methods
    - Possibly a type for `Callable[[], List[Action]]`
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
