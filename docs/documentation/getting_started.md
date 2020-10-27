# Getting started

To use pytailor you need to connect to a Tailor backend. The easiest way to get started
with Tailor is to sign up for a free account at [tailor.wf](https://tailor.wf). For other
options please [contact us](mailto:sales@tailor.wf). In the following it us assumed that
you are using tailor.wf as your backend service.

## Installation

### First time setup
#### 1. Install pytailor
Official releases of pytailor are available on PyPI and can easily be installed with pip:
```
pip install pytailor
```

???+ note
    You can also clone the repository on github and install pytailor 
    with [poetry](https://python-poetry.org/):
    ```
    git clone https://github.com/entailor/pytailor.git
    ``` 
    Then, from the project root run:
    ```
    poetry install
    ``` 
    To install without development dependencies:
    ```
    poetry install --no-dev
    ``` 

#### 2. Configure backend
When pytailor is installed you can use the CLI to set up a barebone config file:
```
tailor init
```

This command generates a config file `.tailor/config.toml` under your home directory with
the following content:

``` toml
[pytailor]
API_WORKER_ID = "<API WORKER ID HERE>"
API_SECRET_KEY = "<API SECRET KEY HERE>"

[worker.my_config]
sleep = 3
ncores = 7
workername = "my_worker"
project_ids = []
capabilities = []

```

Before you can start using pyTailor you need to fill in values for `API_WORKER_ID` and `API_SECRET_KEY` in the config file. These values can be found in the [profile page](https://tailor.wf/settings/profile) for your user on Tailor.wf.


!!! note
    It is also possible to configure pytailor with environmental variables by prefixing
    the environmental variables with `PYTAILOR_`. E.g. to set the API secret key, put it in an environmental variable called `PYTAILOR_API_SECRET_KEY`.


#### 3. Testing
Once you are setup you can start working through the [tutorials](../tutorials/example01_hello_world.md).
