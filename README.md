# tfmod

## potential commands - based loosely on relevant commands from npm

- adduser
- clean-install
- config
- dist-tag
- docs - open terraform registry page in web browser
- doctor - check health
- exec - run a command
- init
- login - for logging into github, terraform registry, etc
- logout
- ping - ping the various apis
- profile - edit tf registry profile?
- publish - the big one
  - check that git is squeaky clean
  - offer to create git repo if no remote set
  - update repository description
  - do validation checks
  - create git tags
  - publish branch and tags
  - if possible, hit publish endpoint in terraform api
- repo - open github repo in web browser
- run - run a script
  - 
- test - run the test script
- unpublish - remove git tag? I dunno
- validate
  - make sure everything follows standard module structure
  - check github for description
  - check that repo matches naming convention
  - check that provider is valid
- version
- whoami - who am I logged in as?
- fmt
- lint

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
