# tfmod

## TODOs

- [ ] infer init params from directory name
- [ ] store terraform state in directory and swap it in/out
- [ ] auto-approve flag
- [ ] module spec addons
  - namespace
  - git main branch
  - private flag (behavior TK as I learn the registry's restrictions)
- [ ] bash shituation
  - [ ] separate files
  - [ ] combine with terraform templating
- [ ] stub commands for things implemented in bash
- [ ] confirm prompt
  - clean up bash impl
- [ ] config
  - git prefer https or ssh
  - git prefer main branch
- [ ] publish
  - module.tfvars
    - if no exist, exit and insist on a `tfmod init`
    - validate defined properties
    - validate/parse version
  - git repository
    - if not a repo, git init
    - validate that branch is main branch
      - warn/confirm before continuing
    - if dirty, prompt for add and commit
    - git repo should be clean
  - github repository
    - construct repo name from module.tfvars
      - warn if directory name does not match what's in module.tfvars
    - if a git remote for github
      - parse/safe remote name
      - parse repo
    - if github repo does not exist
      - shell into `gh` to create it
      - add as remote
    - check/update description based on module.tfvars
  - validate git/github related things
    - module.tfvars vs directory name
    - module.tfvars vs github repo name
    - module.tfvars vs git remote url
  - validate module structure
    - <https://developer.hashicorp.com/terraform/language/modules/develop/structure>
  - tagenpush
    - create x.y.z tag
    - create/force x.y tag
    - create/force x tag
    - TODO: dist tag? how does npm do this?
    - git push origin main --tags
  - if package not on registry api (and not private)
    - open page for publishing
- [ ] tests
  - do after publish is working, since that's the main functionality and the
    APIs should have solidified by then
  - do them for bash too
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
