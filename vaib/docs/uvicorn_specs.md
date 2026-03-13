# Uvicorn Documentation

## Overview

Uvicorn is an ASGI web server implementation for Python. Until recently Python has lacked a minimal low-level server/application interface for async frameworks. The ASGI specification fills this gap, and means we're now able to start building a common set of tooling usable across all async frameworks.

Uvicorn currently supports HTTP/1.1 and WebSockets.

## Installation

Uvicorn is available on PyPI so installation is as simple as:

```
pip install uvicorn
```

## Quickstart

Let's create a simple ASGI application to run with Uvicorn:

main.py
```
async def app(scope, receive, send):
    assert scope['type'] == 'http'
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            (b'content-type', b'text/plain'),
            (b'content-length', b'13'),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello, world!',
    })
```

Then we can run it with Uvicorn:

```
uvicorn main:app
```

## Usage

### Command Line Options

The uvicorn command line tool is the easiest way to run your application.

Common options:
- `--host` - Bind socket to this host. Use `--host 0.0.0.0` to make the application available on your local network. **Default:** '127.0.0.1'.
- `--port` - Bind to a socket with this port. **Default:** 8000.
- `--reload` - Enable auto-reload. **Default:** False.
- `--workers` - Number of worker processes. **Default:** 1.
- `--log-level` - Set the log level. **Options:** 'critical', 'error', 'warning', 'info', 'debug', 'trace'. **Default:** 'info'.
- `--loop` - Set the event loop implementation. **Options:** 'auto', 'asyncio', 'uvloop'. **Default:** 'auto'.
- `--http` - Set the HTTP protocol implementation. **Options:** 'auto', 'h11', 'httptools'. **Default:** 'auto'.

### Running Programmatically

There are several ways to run uvicorn directly from your application.

#### uvicorn.run

If you're looking for a programmatic equivalent of the `uvicorn` command line interface, use `uvicorn.run()`:

```python
import uvicorn

async def app(scope, receive, send):
    ...

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")
```

#### Config and Server instances

For more control over configuration and server lifecycle, use `uvicorn.Config` and `uvicorn.Server`:

```python
import uvicorn

async def app(scope, receive, send):
    ...

if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    server.run()
```

If you'd like to run Uvicorn from an already running async environment, use `uvicorn.Server.serve()` instead:

```python
import asyncio
import uvicorn

async def app(scope, receive, send):
    ...

async def main():
    config = uvicorn.Config("main:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Methods

There are three ways to configure Uvicorn:

1. **Command Line**: Use command line options when running Uvicorn directly.
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Programmatic**: Use keyword arguments when running programmatically with `uvicorn.run()`.
   ```python
   uvicorn.run("main:app", host="0.0.0.0", port=8000)
   ```

3. **Environment Variables**: Use environment variables with the prefix `UVICORN_`.
   ```
   export UVICORN_HOST="0.0.0.0"
   export UVICORN_PORT="8000"
   uvicorn main:app
   ```

CLI options and the arguments for `uvicorn.run()` take precedence over environment variables.

## Development Options

* `--reload` - Enable auto-reload. Uvicorn supports two versions of auto-reloading behavior enabled by this option. **Default:** False.
* `--reload-dir` - Specify which directories to watch for python file changes. May be used multiple times. If unused, then by default the whole current directory will be watched.
* `--reload-delay` - Delay between previous and next check if application needs to be reloaded. **Default:** 0.25.

For more nuanced control over which file modifications trigger reloads, install `uvicorn[standard]`, which includes watchfiles as a dependency.

## Production Options

* `--workers` - Number of worker processes. Defaults to the `$WEB_CONCURRENCY` environment variable if available, or 1. Not valid with `--reload`.
* `--env-file` - Environment configuration file for the ASGI application. **Default:** None.
* `--timeout-worker-healthcheck` - Maximum number of seconds to wait for a worker to respond to a healthcheck. **Default:** 5.

Note: The `--reload` and `--workers` arguments are mutually exclusive. You cannot use both at the same time.

## Logging Options

* `--log-config` - Logging configuration file. **Options:** `dictConfig()` formats: .json, .yaml.
* `--log-level` - Set the log level. **Options:** 'critical', 'error', 'warning', 'info', 'debug', 'trace'. **Default:** 'info'.
* `--no-access-log` - Disable access log only, without changing log level.
* `--use-colors / --no-use-colors` - Enable / disable colorized formatting of the log records.

## Implementation Options

* `--loop` - Set the event loop implementation. The uvloop implementation provides greater performance, but is not compatible with Windows or PyPy. **Options:** 'auto', 'asyncio', 'uvloop'. **Default:** 'auto'.
* `--http` - Set the HTTP protocol implementation. The httptools implementation provides greater performance, but it not compatible with PyPy. **Options:** 'auto', 'h11', 'httptools'. **Default:** 'auto'.
* `--ws` - Set the WebSockets protocol implementation. **Options:** 'auto', 'none', 'websockets', 'websockets-sansio', 'wsproto'. **Default:** 'auto'.
* `--ws-max-size` - Set the WebSockets max message size, in bytes. **Default:** 16777216 (16 MB).
* `--ws-max-queue` - Set the maximum length of the WebSocket incoming message queue. **Default:** 32.
* `--ws-ping-interval` - Set the WebSockets ping interval, in seconds. **Default:** 20.0.
* `--ws-ping-timeout` - Set the WebSockets ping timeout, in seconds. **Default:** 20.0.
* `--lifespan` - Set the Lifespan protocol implementation. **Options:** 'auto', 'on', 'off'. **Default:** 'auto'.

## HTTP Options

* `--root-path` - Set the ASGI `root_path` for applications submounted below a given URL path.
* `--proxy-headers / --no-proxy-headers` - Enable/Disable X-Forwarded-Proto, X-Forwarded-For to populate remote address info.
* `--forwarded-allow-ips` - Comma separated list of IP Addresses, IP Networks, or literals to trust with proxy headers. Defaults to the `$FORWARDED_ALLOW_IPS` environment variable if available, or '127.0.0.1'.
* `--server-header / --no-server-header` - Enable/Disable default `Server` header. **Default:** True.
* `--date-header / --no-date-header` - Enable/Disable default `Date` header. **Default:** True.

## HTTPS Options

The SSL context can be configured with the following options:
* `--ssl-keyfile` - The SSL key file.
* `--ssl-keyfile-password` - The password to decrypt the ssl key.
* `--ssl-certfile` - The SSL certificate file.
* `--ssl-version` - The SSL version to use. **Default:** ssl.PROTOCOL_TLS_SERVER.
* `--ssl-cert-reqs` - Whether client certificate is required. **Default:** ssl.CERT_NONE.
* `--ssl-ca-certs` - The CA certificates file.
* `--ssl-ciphers` - The ciphers to use. **Default:** "TLSv1".

## Resource Limits and Timeouts

* `--limit-concurrency` - Maximum number of concurrent connections or tasks to allow, before issuing HTTP 503 responses.
* `--limit-max-requests` - Maximum number of requests to service before terminating the process.
* `--backlog` - Maximum number of connections to hold in backlog. **Default:** 2048.
* `--timeout-keep-alive` - Close Keep-Alive connections if no new data is received within this timeout (in seconds). **Default:** 5.
* `--timeout-graceful-shutdown` - Maximum number of seconds to wait for graceful shutdown.