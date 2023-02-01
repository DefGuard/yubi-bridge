# YubiBridge

[User Documentation](https://defguard.gitbook.io/defguard/enterprise-features/yubikey-provisioning)

We created YubiBridge to make creating and provisioning of [GPG](https://gnupg.org/) keys for [YubiKey](https://www.yubico.com/products/) easy.
YubiBridge allows you to provision your YubiKey with automatically generated GPG keys in a few simple steps.
It's completely safe, we are not storing private keys, they are completely wiped after provisioning.
Only public SSH and PGP keys are sent to Defguard - you can download them at any time.

## How to use YubiBridge?

You can use YubiBridge in two ways:

* [as a Defguard client service](#as-a-defguard-client) - run the service and then provision YubiKey from Defguard web app
* [as a standalone command-line application](#as-a-cli-app) - insert your YubiKey then run the app providing your name and email as arguments

### As a Defguard client

You can see available provisioners in Defguard web-application under "provisioners" tab.

To start your own provisioner:

1. Clone YubiBridge repository:

```
git clone --recursive git@github.com:DefGuard/yubi-bridge.git && cd yubi-bridge
```

2. Copy and fill in the .env file:

```
cp .env.template .env
```

Variables to set:

* `DEFGUARD_URL`: Defguard GRPC URL, e.g.: `defguard-grpc.mycompany.com`
* `WORKER_ID`: Your machine id, this is the name you'll see in Defguard "provisioners" tab, e.g.: `Jane-Laptop`
* `DEFGUARD_TOKEN`: Token from Defguard app to secure gRPC connection available on provisioners page.

> You can find list of all environment variables and arguments with explanation [here](../in-depth/environmental-variables-configuration.md).

3. Finally, run the service with docker-compose:

```
docker compose run yubi-bridge --grpc --worker-token <TOKEN>
```

> You'll find the token on "Provisioners" page of your Defguard instance.

If everything went well, your machine (with worker id you just set) should be visible in Defguard provisioners tab.
### 3. Environmental variables

| Environmental variable        | Default             | Description                                                                |
| ----------------------------- | ------------------- | -------------------------------------------------------------------------- |
| WORKER_ID                     | YubiBridge          | Worker id                                                                  |
| LOG_LEVEL                     | INFO                | Logging level, available levels are:    INFO,DEBUG,ERROR                   |
| URL                           | localhost:50055     | Url of your DefGuard instance                                              |
| JOB_INTERVAL                  | 2                   | Number of seconds in which worker ping DefGuard for data to provision      |
| SMARTCARD_RETRIES             | 1                   | Number of retries in case if there are no smartcards                       |
| SMARTCARD_RETRY_INTERVAL      | 15                  | Number of seconds before checking for smartcard again                      |
