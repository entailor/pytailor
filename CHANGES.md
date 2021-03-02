#Release notes

### NEXT (Feature coming in next release, currently in master branch)
- Nothing yet

### 0.3.2
- Add support for Python 3.9
- Replace yaql in favour of jsonpath-ng for parsing query expressions
- Support nested query expressions in *args* and *kwargs* arguments to PythonTask (see example 11)
- Bugfixes

### 0.3.1
- Improve error logging for worker

### 0.3.0
- Adapt to REST-API version 2.0.0
- Create WorkflowDefinition from existing workflow (see example 10)

### 0.2.3
- Set default backend to https://api.tailor.wf/
- Remove API_IDP_URL and API_CLIENT_ID from config.toml created by `tailor init` command

### 0.2.2
- updated docs
- better handling of file upload/download
- update default IDP config values, matching new prod environment for Tailor.wf
- improved error messages on http status errors