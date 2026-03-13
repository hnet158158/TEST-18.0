# FastAPI Documentation

*FastAPI framework, high performance, easy to learn, fast to code, ready for production*

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.

The key features are:

* **Fast**: Very high performance, on par with **NodeJS** and **Go** (thanks to Starlette and Pydantic). [One of the fastest Python frameworks available](#performance).
* **Fast to code**: Increase the speed to develop features by about 200% to 300%. *
* **Fewer bugs**: Reduce about 40% of human (developer) induced errors. *
* **Intuitive**: Great editor support. Completion everywhere. Less time debugging.
* **Easy**: Designed to be easy to use and learn. Less time reading docs.
* **Short**: Minimize code duplication. Multiple features from each parameter declaration. Fewer bugs.
* **Robust**: Get production-ready code. With automatic interactive documentation.
* **Standards-based**: Based on (and fully compatible with) the open standards for APIs: [OpenAPI](https://github.com/OAI/OpenAPI-Specification) (previously known as Swagger) and [JSON Schema](https://json-schema.org/).

* estimation based on tests conducted by an internal development team, building production applications.

## Installation

Create and activate a [virtual environment](https://fastapi.tiangolo.com/virtual-environments/) and then install FastAPI:

```
$ pip install "fastapi[standard]"
```

**Note**: Make sure you put `"fastapi[standard]"` in quotes to ensure it works in all terminals.

## Example

### Create it

Create a file `main.py` with:

```
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

Or use `async def`...

If your code uses `async` / `await`, use `async def`:

```
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Run it

Run the server with:

```
$ fastapi dev
```

About the command `fastapi dev`...

The command `fastapi dev` reads your `main.py` file automatically, detects the **FastAPI** app in it, and starts a server using [Uvicorn](https://www.uvicorn.dev).

By default, `fastapi dev` will start with auto-reload enabled for local development.

You can read more about it in the [FastAPI CLI docs](https://fastapi.tiangolo.com/fastapi-cli/).

### Check it

Open your browser at <http://127.0.0.1:8000/items/5?q=somequery>.

You will see the JSON response as:

```
{"item_id": 5, "q": "somequery"}
```

You already created an API that:

* Receives HTTP requests in the *paths* `/` and `/items/{item_id}`.
* Both *paths* take `GET` *operations* (also known as HTTP *methods*).
* The *path* `/items/{item_id}` has a *path parameter* `item_id` that should be an `int`.
* The *path* `/items/{item_id}` has an optional `str` *query parameter* `q`.

### Interactive API docs

Now go to <http://127.0.0.1:8000/docs>.

You will see the automatic interactive API documentation (provided by [Swagger UI](https://github.com/swagger-api/swagger-ui)).

### Alternative API docs

And now, go to <http://127.0.0.1:8000/redoc>.

You will see the alternative automatic documentation (provided by [ReDoc](https://github.com/Rebilly/ReDoc)).

## Example upgrade

Now modify the file `main.py` to receive a body from a `PUT` request.

Declare the body using standard Python types, thanks to Pydantic.

```
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
```

The `fastapi dev` server should reload automatically.

## Main Features

In summary, you declare **once** the types of parameters, body, etc. as function parameters.

You do that with standard modern Python types.

You don't have to learn a new syntax, the methods or classes of a specific library, etc.

Just standard **Python**.

For example, for an `int`:

```
item_id: int
```

or for a more complex `Item` model:

```
item: Item
```

...and with that single declaration you get:

* Editor support, including:
  + Completion.
  + Type checks.
* Validation of data:
  + Automatic and clear errors when the data is invalid.
  + Validation even for deeply nested JSON objects.
* Conversion of input data: coming from the network to Python data and types. Reading from:
  + JSON.
  + Path parameters.
  + Query parameters.
  + Cookies.
  + Headers.
  + Forms.
  + Files.
* Conversion of output data: converting from Python data and types to network data (as JSON):
  + Convert Python types (`str`, `int`, `float`, `bool`, `list`, etc).
  + `datetime` objects.
  + `UUID` objects.
  + Database models.
  + ...and many more.
* Automatic interactive API documentation, including 2 alternative user interfaces:
  + Swagger UI.
  + ReDoc.

Coming back to the previous code example, **FastAPI** will:

* Validate that there is an `item_id` in the path for `GET` and `PUT` requests.
* Validate that the `item_id` is of type `int` for `GET` and `PUT` requests.
  + If it is not, the client will see a useful, clear error.
* Check if there is an optional query parameter named `q` (as in `http://127.0.0.1:8000/items/foo?q=somequery`) for `GET` requests.
  + As the `q` parameter is declared with `= None`, it is optional.
  + Without the `None` it would be required (as is the body in the case with `PUT`).
* For `PUT` requests to `/items/{item_id}`, read the body as JSON:
  + Check that it has a required attribute `name` that should be a `str`.
  + Check that it has a required attribute `price` that has to be a `float`.
  + Check that it has an optional attribute `is_offer`, that should be a `bool`, if present.
  + All this would also work for deeply nested JSON objects.
* Convert from and to JSON automatically.
* Document everything with OpenAPI, that can be used by:
  + Interactive documentation systems.
  + Automatic client code generation systems, for many languages.
* Provide 2 interactive documentation web interfaces directly.

## Dependencies

FastAPI depends on Pydantic and Starlette.

### Standard Dependencies

When you install FastAPI with `pip install "fastapi[standard]"` it comes with the `standard` group of optional dependencies:

Used by Pydantic:
* `email-validator` - for email validation.

Used by Starlette:
* `httpx` - Required if you want to use the `TestClient`.
* `jinja2` - Required if you want to use the default template configuration.
* `python-multipart` - Required if you want to support form "parsing", with `request.form()`.

Used by FastAPI:
* `uvicorn` - for the server that loads and serves your application. This includes `uvicorn[standard]`, which includes some dependencies (e.g. `uvloop`) needed for high performance serving.
* `fastapi-cli[standard]` - to provide the `fastapi` command.
  + This includes `fastapi-cloud-cli`, which allows you to deploy your FastAPI application to [FastAPI Cloud](https://fastapicloud.com).

## Tutorial - User Guide

This tutorial shows you how to use **FastAPI** with most of its features, step by step.

Each section gradually builds on the previous ones, but it's structured to separate topics, so that you can go directly to any specific one to solve your specific API needs.

It is also built to work as a future reference so you can come back and see exactly what you need.

### Run the code

All the code blocks can be copied and used directly (they are actually tested Python files).

To run any of the examples, copy the code to a file `main.py`, and start `fastapi dev`:

```
$ fastapi dev
```

It is **HIGHLY encouraged** that you write or copy the code, edit it and run it locally.

Using it in your editor is what really shows you the benefits of FastAPI, seeing how little code you have to write, all the type checks, autocompletion, etc.