# Pydantic Settings 2.0 Documentation

## Overview

Pydantic Settings provides optional Pydantic features for loading a settings or config class from environment variables or secrets files.

## Installation

Installation is as simple as:
```
pip install pydantic-settings
```

## Usage

If you create a model that inherits from `BaseSettings`, the model initialiser will attempt to determine the values of any fields not passed as keyword arguments by reading from the environment. (Default values will still be used if the matching environment variable is not set.)

This makes it easy to:
* Create a clearly-defined, type-hinted application configuration class
* Automatically read modifications to the configuration from environment variables
* Manually override specific settings in the initialiser where desired (e.g. in unit tests)

For example:

```python
from collections.abc import Callable
from typing import Any
from pydantic import (
    AliasChoices, AmqpDsn, BaseModel, Field, ImportString, PostgresDsn, RedisDsn,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

class SubModel(BaseModel):
    foo: str = 'bar'
    apple: int = 1

class Settings(BaseSettings):
    auth_key: str = Field(validation_alias='my_auth_key')  # The environment variable `my_auth_key` will be read instead of `auth_key`
    api_key: str = Field(alias='my_api_key')  # The environment variable `my_api_key` will be used for both validation and serialization
    redis_dsn: RedisDsn = Field(
        'redis://user:pass@localhost:6379/1',
        validation_alias=AliasChoices('service_redis_dsn', 'redis_url'),  # Multiple environment variable names for a single field
    )
    pg_dsn: PostgresDsn = 'postgres://user:pass@localhost:5432/foobar'
    amqp_dsn: AmqpDsn = 'amqp://user:pass@localhost:5672/'
    special_function: ImportString[Callable[[Any], Any]] = 'math.cos'  # Import an object from a string
    # to override domains: export my_prefix_domains='["foo.com", "bar.com"]'
    domains: set[str] = set()
    # to override more_settings: export my_prefix_more_settings='{"foo": "x", "apple": 1}'
    more_settings: SubModel = SubModel()
    
    model_config = SettingsConfigDict(env_prefix='my_prefix_')  # Set a prefix for all environment variables
```

## Validation of Default Values

Unlike pydantic `BaseModel`, default values of `BaseSettings` fields are validated by default. You can disable this behaviour by setting `validate_default=False` either in `model_config` or on field level by `Field(validate_default=False)`:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False)  # default won't be validated
    foo: int = 'test'
    print(Settings())  #> foo='test'
```

## Environment Variable Names

By default, the environment variable name is the same as the field name.

You can change the prefix for all environment variables by setting the `env_prefix` config setting:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='my_prefix_')
    auth_key: str = 'xxx'  # will be read from `my_prefix_auth_key`
```

The default `env_prefix` is `''` (empty string).

If you want to change the environment variable name for a single field, you can use an alias:
* Using `Field(alias=...)`
* Using `Field(validation_alias=...)`

### Case Sensitivity

By default, environment variable names are case-insensitive.

If you want to make environment variable names case-sensitive, you can set the `case_sensitive` config setting:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    redis_host: str = 'localhost'
```

## Parsing Environment Variable Values

By default environment variables are parsed verbatim, including if the value is empty. You can choose to ignore empty environment variables by setting the `env_ignore_empty` config setting to `True`.

Complex types like `list`, `set`, `dict`, and sub-models are populated from the environment by treating the environment variable's value as a JSON-encoded string.

Another way to populate nested complex variables is to configure your model with the `env_nested_delimiter` config setting, then use an environment variable with a name pointing to the nested module fields. What it does is simply explodes your variable into nested models or dicts. So if you define a variable `FOO__BAR__BAZ=123` it will convert it into `FOO={'BAR': {'BAZ': 123}}`.

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DeepSubModel(BaseModel):
    v4: str

class SubModel(BaseModel):
    v1: str
    v2: bytes
    v3: int
    deep: DeepSubModel

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter='__')
    v0: str
    sub_model: SubModel
```

## Dotenv (.env) Support

Dotenv files (generally named `.env`) are a common pattern that make it easy to use environment variables in a platform-independent manner.

A dotenv file follows the same general principles of all environment variables, and it looks like this:

.env
```
# ignore comment
ENVIRONMENT="production"
REDIS_ADDRESS=
MEANING_OF_LIFE=42
MY_VAR='Hello world'
```

Once you have your `.env` file filled with variables, *pydantic* supports loading it in two ways:

1. Setting the `env_file` (and `env_file_encoding` if you don't want the default encoding of your OS) on `model_config` in the `BaseSettings` class:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
```

2. Instantiating the `BaseSettings` derived class with the `_env_file` keyword argument (and the `_env_file_encoding` if needed):

```python
settings = Settings(_env_file='prod.env', _env_file_encoding='utf-8')
```

Even when using a dotenv file, *pydantic* will still read environment variables as well as the dotenv file, **environment variables will always take priority over values loaded from a dotenv file**.

## Secrets

Placing secret values in files is a common pattern to provide sensitive configuration to an application.

A secret file follows the same principal as a dotenv file except it only contains a single value and the file name is used as the key.

To use secrets, set the `secrets_dir` on `model_config` in a `BaseSettings` class to the directory where your secret files are stored:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/var/run')
    database_password: str
```

Even when using a secrets directory, *pydantic* will still read environment variables from a dotenv file or the environment, **a dotenv file and environment variables will always take priority over values loaded from the secrets directory**.

## Field Value Priority

In the case where a value is specified for the same `Settings` field in multiple ways, the selected value is determined as follows (in descending order of priority):

1. Arguments passed to the `Settings` class initialiser.
2. Environment variables, e.g. `my_prefix_special_function` as described above.
3. Variables loaded from a dotenv (`.env`) file.
4. Variables loaded from the secrets directory.
5. The default field values for the `Settings` model.

## Customising Settings Sources

If the default order of priority doesn't match your needs, it's possible to change it by overriding the `settings_customise_sources` method of your `Settings`.

`settings_customise_sources` takes four callables as arguments and returns any number of callables as a tuple. In turn these callables are called to build the inputs to the fields of the settings class.

Each callable should take an instance of the settings class as its sole argument and return a `dict`.

The order of the returned callables decides the priority of inputs; first item is the highest priority.

```python
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

class Settings(BaseSettings):
    database_dsn: PostgresDsn
    
    @classmethod
    def settings_customise_sources(cls, settings_cls: type[BaseSettings], init_settings: PydanticBaseSettingsSource, env_settings: PydanticBaseSettingsSource, dotenv_settings: PydanticBaseSettingsSource, file_secret_settings: PydanticBaseSettingsSource) -> tuple[PydanticBaseSettingsSource,...]:
        return env_settings, init_settings, file_secret_settings
```

By flipping `env_settings` and `init_settings`, environment variables now have precedence over `__init__` kwargs.