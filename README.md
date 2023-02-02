# YubiBridge

[Docs](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning)

Yubi-Bridge is a Python module that creates [GPG](https://gnupg.org/) keys for
[YubiKey](https://www.yubico.com/products/) and transfers them automatically to YubiKey.
It can be run as a stand-alone application, or a client that takes jobs from DefGuard Core backend.
Refer to [documentation](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning) for more info.

## How to run?

### 1. Using poetry:

> Make sure you have [Poetry](https://python-poetry.org/) installed.

```
# Clone the repository recursively (with protobuf files)
git clone --recursive git@github.com:DefGuard/yubi-bridge.git
cd yubi-bridge

# Install dependencies
poetry install

# Compile proto files
poetry run python3 -m grpc_tools.protoc -Iproto --python_out=yubi-bridge --grpc_python_out=yubi-bridge proto/worker/worker.proto

# Run YubiBridge
poetry run python3 yubi-bridge/main.py [options]
```

### 2. Using docker-compose

Refer to [documentation](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning#as-a-defguard-client)
for a guide on how to setup docker-compose.

#### 3. Environmental variables

| Environmental variable        | Default             | Description                                                                |
| ----------------------------- | ------------------- | -------------------------------------------------------------------------- |
| WORKER_ID                     | YubiBridge          | Worker id                                                                  |
| LOG_LEVEL                     | INFO                | Logging level, available levels are:    INFO,DEBUG,ERROR                   |
| URL                           | localhost:50055     | Url of your DefGuard instance                                              |
| JOB_INTERVAL                  | 2                   | Number of seconds in which worker ping DefGuard for data to provision      |
| SMARTCARD_RETRIES             | 1                   | Number of retries in case if there are no smartcards                       |
| SMARTCARD_RETRY_INTERVAL      | 15                  | Number of seconds before checking for smartcard again                      |
