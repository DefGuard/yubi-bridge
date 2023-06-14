# YubiBridge

[Docs](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning)

Yubi-Bridge is a Python module that creates [GPG](https://gnupg.org/) keys for
[YubiKey](https://www.yubico.com/products/) and transfers them automatically to YubiKey.
It can be run as a stand-alone application, or a client that takes jobs from DefGuard Core backend.
Refer to [documentation](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning) for more info.

## How to run?

You can run this code:

* using poetry - recommended for development
* using docker-compose - recommended for regular use

### Using poetry:

> Make sure you have [Poetry](https://python-poetry.org/) installed.

```
# Clone the repository recursively (with protobuf files)
git clone --recursive git@github.com:DefGuard/yubi-bridge.git
cd yubi-bridge

# get protos
git submodule init
git submodule update

# Install dependencies
poetry install

# Compile proto files
poetry run python3 -m grpc_tools.protoc -Iproto --python_out=yubi-bridge --grpc_python_out=yubi-bridge proto/worker/worker.proto

# Run YubiBridge
poetry run python3 yubi-bridge/main.py [options]
```

Example, running as a Defguard client:

```
poetry run python3 yubi-bridge/main.py --grpc defguard-grpc.mycompany.com --worker-token <YOUR_JWT_TOKEN> --id dev_worker
```

> You'll find the JWT token on "Provisioners" page of your Defguard instance.

Example, running as a stand-alone app:

```
poetry run python3 yubi-bridge/main.py --provision <first_name> <last_name> <email>
```

### Using docker-compose

Refer to [documentation](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning#as-a-defguard-client)
for a guide on how to setup docker-compose.

## Environmental variables

You can set these variables to configure how the YubiBridge behaves.

| Environmental variable        | Default             | Description                                                                |
| ----------------------------- | ------------------- | -------------------------------------------------------------------------- |
| WORKER_ID                     | YubiBridge          | Worker id                                                                  |
| LOG_LEVEL                     | INFO                | Logging level, available levels are:    INFO,DEBUG,ERROR                   |
| URL                           | localhost:50055     | Url of your DefGuard instance                                              |
| JOB_INTERVAL                  | 2                   | Number of seconds in which worker ping DefGuard for data to provision      |
| SMARTCARD_RETRIES             | 1                   | Number of retries in case if there are no smartcards                       |
| SMARTCARD_RETRY_INTERVAL      | 15                  | Number of seconds before checking for smartcard again                      |
