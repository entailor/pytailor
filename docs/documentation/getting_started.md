# Getting started

To use Pytailor you need to connect to a Tailor backend. The easiest way to get started
with Tailor is to sign up for a free account at [Tailor.wf](https://tailor.wf). For other
options please [contact us](mailto:sales@tailor.wf). In the following it us assumed that
you are using Tailor.wf as your backend service.

## Installation

### First time setup
#### 1. Install pytailor
Official releases of pytailor are available on pypi and can easily be installed with pip:
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
When pytailor is installed your ca use the CLI to set up a barebone config file:
```
tailor init
```

This command generates a config file `.tailor/config.toml` under your home directory with
the following content:

``` toml
API_KEY = <API KEY GOES HERE>
API_BASE_URL = <URL FOR THE BACKEND REST API GOES HERE>
```

???+ note
    It is also possible to configure pytailor with environmental variables by prefixing
    the environmental variables with `PYTAILOR_`. E.g. to set the API, key put it in an
    environmental variable called `PYTAILOR_API_KEY`.


### Update Pytailor




## Basic usage

With Pytailor installed and a backend properly configured you should be able to run the
following example:

``` python

from tailor import PythonTask, DAG

```

In this example, several key concepts are illustrated:

... walk through code...


Please consult the Consepts page...