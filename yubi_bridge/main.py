import argparse
import logging
import re
from os import getenv
from pathlib import Path
from subprocess import Popen, PIPE, run, CalledProcessError
from tempfile import TemporaryDirectory
from time import sleep
from typing import Tuple

import gnupg
import pexpect
from ykman.device import list_all_devices

from .client import WorkerHandler

URL = getenv("URL", "localhost:50055")
WORKER_ID = getenv("WORKER_ID", "YubiBridge")
DEFGUARD_TOKEN = getenv("DEFGUARD_TOKEN", "DEFGUARD_TOKEN")
LOG_LEVEL = getenv("LOG_LEVEL", logging.INFO)
SMARTCARD_RETRIES = getenv("RETRIES", 1)
JOB_INTERVAL = getenv("JOB_INTERVAL", 2)
SMARTCARD_RETRY_INTERVAL = getenv("SMARTCARD_INTERVAL", 15)

LOG = logging.getLogger(__name__)


class YubiBridge:
    def __init__(self, command: str = None):
        """Create homedir and initialise GPG with it."""
        # Try to kill default gpg-agent, which might interfere with our homedir.
        comp_proc = run(
            ["gpgconf", "--kill", "gpg-agent"],
            capture_output=True,
            check=True,
            text=True,
        )
        if comp_proc.stderr:
            LOG.error(comp_proc.stderr)
        if comp_proc.stdout:
            LOG.debug(comp_proc.stdout)

        self.tempdir = TemporaryDirectory()
        self.homedir = self.tempdir.name
        LOG.debug("Temporary directory %s", self.homedir)
        self.gpg = gnupg.GPG(gnupghome=self.homedir)
        self.gpg.encoding = "utf-8"
        # TODO: probably not needed when master key is going to be discarded
        self.passphrase = "password"
        self.pin = "123456"  # default PIN
        self.admin_pin = "12345678"  # default admin PIN
        self.command = command

    def keys_exist(self) -> bool:
        """Checks if GnuPG keychain contains any keys."""
        return bool(self.gpg.list_keys())

    def delete_keypair(self, fingerprint):
        """Delete private and public key for a given fingerprint."""
        LOG.debug("Deleting private key %s", fingerprint)
        self.gpg.delete_keys(fingerprint, True, passphrase=self.passphrase)
        LOG.debug("Deleting public key %s", fingerprint)
        self.gpg.delete_keys(fingerprint)

    def delete_all_keys(self):
        """Delete all keys from GnuPG keychain."""
        for key in self.gpg.list_keys():
            self.delete_keypair(key["fingerprint"])

    def create_keypair(self, name: str, email: str) -> str:
        """Create private/public key pair. Return key fingerprint."""
        # Generate master key for signing and a sub-key for encryption.
        LOG.info("Creating keys for %s %s", name, email)
        input_data = self.gpg.gen_key_input(
            key_type="RSA",
            key_length=4096,
            key_usage="sign,cert",  # encr, sign, auth, cert
            name_real=name,
            name_email=email,
            passphrase=self.passphrase,
            expire_date=0,  # key does not expire
            subkey_type="RSA",
            subkey_length=4096,
            subkey_usage="encr",
        )

        LOG.debug("Creating master key")
        master_key = self.gpg.gen_key(input_data)

        # Generate sub-key for authentication
        # TODO: this fails with 'TypeError: expected str, bytes or
        # os.PathLike object, not GenKey'
        # subkey = self.gpg.add_subkey(master_key,
        #  master_passphrase=self.passphrase, usage="auth")
        args = [
            self.gpg.gpgbinary,
            "--homedir",
            self.homedir,
            "--pinentry-mode=loopback",
            "--no-tty",
            "--passphrase",
            self.passphrase,
            "--quick-add-key",
            master_key.fingerprint,
            "rsa4096",
            "auth",
        ]
        LOG.debug("Running %s", " ".join(args))
        comp_proc = run(args, capture_output=True, check=True, text=True)
        if comp_proc.stderr:
            LOG.error(comp_proc.stderr)
        if comp_proc.stdout:
            LOG.debug(comp_proc.stdout)

        # sanity check
        expected_subs = [
            key
            for key in self.gpg.list_keys()
            if key["fingerprint"] == master_key.fingerprint
        ][0]["subkeys"]
        assert len(expected_subs) == 2

        LOG.debug("Created key %s", master_key.fingerprint)
        return master_key.fingerprint

    def public_key(self, fingerprint: str) -> str:
        """Return public key for a given fingerprint."""
        # KeyID is last 16 hex digits of fingerprint.
        return self.gpg.export_keys(fingerprint[-16:])

    def private_key(self, fingerprint: str) -> str:
        """Return private key for a given fingerprint."""
        # KeyID is last 16 hex digits of fingerprint.
        return self.gpg.export_keys(fingerprint[-16:], True, passphrase=self.passphrase)

    def ssh_key(self, fingerprint: str) -> str:
        """Return public key for in SSH format."""
        # FIXME: not implemented in python-gnupg
        args = [
            self.gpg.gpgbinary,
            "--homedir",
            self.homedir,
            "--export-ssh-key",
            fingerprint[-16:],
        ]
        LOG.debug("Running %s", " ".join(args))
        comp_proc = run(args, capture_output=True, check=True, text=True)
        if comp_proc.stderr:
            LOG.error(comp_proc.stderr)
        return comp_proc.stdout

    def check_connection(self):
        """Check if any smartcard is connected"""
        self.restart_pcscd()
        LOG.debug("Checking for smartcard...")
        try:
            for _, info in list_all_devices():
                LOG.debug("Found device with serial: %s", info.serial)
            return len(list_all_devices()) != 0
        except Exception:
            LOG.error("Device error")

    def keys_to_card(self, email: str) -> Tuple[bool, str]:
        """Transfer keys to card. Return True on success."""
        # Note: there is no way to point GnuPG to a desired card.
        # expected prompts
        prompt_bool = "\r\n[GNUPG:] GET_BOOL keyedit.keytocard.use_primary\r\n"
        prompt_line = "\r\n[GNUPG:] GET_LINE keyedit.prompt\r\n"
        prompt_pass = "\r\n[GNUPG:] GET_HIDDEN passphrase.enter\r\n"
        prompt_repl = "\r\n[GNUPG:] GET_BOOL cardedit.genkeys.replace_key\r\n"
        prompt_okay = "\r\n[GNUPG:] GET_BOOL keyedit.save.okay\r\n"
        prompt_type = "\r\n[GNUPG:] GET_LINE cardedit.genkeys.storekeytype\r\n"
        LOG.info("Transfering keys to card")
        cmd = pexpect.spawn(
            self.gpg.gpgbinary,
            [
                "--homedir",
                self.homedir,
                "--command-fd=0",
                "--status-fd=2",
                "--batch",
                "--pinentry-mode=loopback",
                "--edit-key",
                email,
            ],
            encoding="utf-8",
            logfile=open("/tmp/yb-log.txt", "w", encoding="utf-8"),
        )
        for prompt, line in (
            # store primary key
            (prompt_line, "keytocard"),
            (prompt_bool, "y"),
            (prompt_type, "1"),
            (prompt_pass, self.passphrase),
            (prompt_pass, self.admin_pin),
            (prompt_pass, self.admin_pin),
            # store encryption key
            (prompt_line, "key 1"),
            (prompt_line, "keytocard"),
            (prompt_type, "2"),
            (prompt_pass, self.passphrase),
            (prompt_pass, self.admin_pin),
            (prompt_line, "key 1"),
            # store authentication key
            (prompt_line, "key 2"),
            (prompt_line, "keytocard"),
            (prompt_type, "3"),
            (prompt_pass, self.passphrase),
            (prompt_pass, self.admin_pin),
            # good-bye
            (prompt_line, "q"),
            (prompt_okay, "y"),
        ):
            index = cmd.expect_exact(
                [prompt, prompt_repl, pexpect.EOF, pexpect.TIMEOUT]
            )
            if index == 1:
                # WARNING: such a key has already been stored on the card!
                err = "Card already has the key"
                LOG.error(err)
                LOG.error(
                    "Reset card to factory settings first with command gpg --card-edit"
                )
                return False, err
            if index == 2:
                err = "GnuPG process disconnected"
                LOG.error(err)
                return False, err
            if index == 3:
                err = "Can't connect to smartcard"
                LOG.error(err)
                return False, err
            cmd.sendline(line)
        # wait for graceful exit, or card info won't be saved
        cmd.expect_exact([pexpect.EOF, pexpect.TIMEOUT])
        LOG.info("Keys have been transferred to card")

        return True, "None"

    def check_yubikey(self) -> bool:
        """Check if keys were added to YubiKey."""
        with Popen(
            [self.gpg.gpgbinary, "--homedir", self.homedir, "--card-status"],
            stdout=PIPE,
        ) as p:
            sout = p.communicate()
            sout = sout[0].decode()
            try:
                result = re.search("(?<=General key info..: )(.*)", sout).group(0)
                if result != "[none]":
                    return True
                print(
                    "Something went wrong.."
                    "Reset yubikey to factory settings and try again"
                )
            except AttributeError:
                print("No gpg keys")

        return False

    def restart_pcscd(self) -> None:
        """Restart smartcard driver if exists"""
        path = Path("/etc/init.d/pcscd")
        if path.exists():
            args = [path, "restart"]
            cmd = run(args, capture_output=True, check=True, text=True)
            LOG.debug(cmd.stdout)

    def run_command(
        self, command: str, firstname: str, lastname: str, ssh_key: str, public_key: str
    ) -> None:
        args = [*command, firstname, lastname, ssh_key, public_key]
        LOG.debug("Running %s", " ".join(args))
        try:
            comp_proc = run(
                args,
                capture_output=True,
                check=True,
                text=True,
            )
            if comp_proc.stderr:
                LOG.error(comp_proc.stderr)
            if comp_proc.stdout:
                LOG.debug(comp_proc.stdout)
        except CalledProcessError as e:
            LOG.error(e.stdout)
            LOG.error(e.stderr)
        LOG.info("Command: %s have finished", " ".join(command))

    def provision(
        self, firstname: str, lastname: str, email: str
    ) -> Tuple[bool, str, str, str, str]:
        """
        Do entire provisioning.
        Return public key in PGP and SSH formats, and key fingerprint.
        """
        self.restart_pcscd()
        fullname = f"{firstname} {lastname}"
        fingerprint = self.create_keypair(fullname, email)
        public_key = self.public_key(fingerprint)
        ssh_key = self.ssh_key(fingerprint)
        # TODO: --card-edit
        success, err = self.keys_to_card(email)
        if success and self.command:
            self.run_command(self.command, firstname, lastname, ssh_key, public_key)
        self.delete_keypair(fingerprint)
        return (success, public_key, ssh_key, fingerprint, err)


def main():
    """Main program entry."""
    parser = argparse.ArgumentParser(
        prog="yubikey-bridge",
        description="DefGuard YubiKey provisioning tool",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p",
        "--provision",
        nargs=3,
        metavar=("<firstname>", "<lastname>", "<email>"),
        help="Provision with the following data",
    )
    group.add_argument(
        "-g",
        "--grpc",
        nargs="?",
        const=f"{URL}",
        help="Connect to gRPC server",
    )
    parser.add_argument(
        "-i",
        "--id",
        default=WORKER_ID,
        help="Worker ID (default: YubiBridge)",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "-s",
        "--secure",
        action="store_true",
        help="Enable secure (TLS) connection to gRPC server",
    )
    parser.add_argument(
        "-w",
        "--worker-token",
        default=DEFGUARD_TOKEN,
        help="Secret worker token to secure gRPC communication",
    )
    parser.add_argument(
        "-c",
        "--command",
        nargs="+",
        help="Run command using keys as arguments",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else LOG_LEVEL,
        format="%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    yb = YubiBridge(args.command)
    if yb.keys_exist():
        LOG.error("Some keys exist in GnuPG tempdir.")
        return

    if args.provision is not None:
        yb.provision(args.provision[0], args.provision[1], args.provision[2])

    if args.grpc is not None:
        LOG.info("Connecting to %s as %s", args.grpc, args.id)
        worker = WorkerHandler(args.id, args.grpc, args.worker_token, args.secure)
        worker.register()
        LOG.info("Worker connected")
        while True:
            job = worker.get_job()
            if job:
                LOG.info(
                    "Received job with id %s to provision yubikey for: %s %s %s",
                    job[3],
                    job[0],
                    job[1],
                    job[2],
                )
                for i in range(int(SMARTCARD_RETRIES) + 1):
                    if yb.check_connection():
                        success, public_key, ssh_key, fingerprint, err = yb.provision(
                            job[0], job[1], job[2]
                        )
                        LOG.info("Sending job status to DefGuard")
                        worker.send_job_status(
                            job[3], success, public_key, ssh_key, fingerprint, err
                        )
                        break

                    LOG.error(
                        "No smartcard found, please insert YubiKey "
                        "or if YubiKey is inserted, re-insert it."
                    )

                    if i == SMARTCARD_RETRIES:
                        LOG.info("Sending job status to DefGuard")
                        worker.send_job_status(
                            job[3],
                            False,
                            "-",
                            "-",
                            "-",
                            "Can't connect to smartcard",
                        )
                        break

                    LOG.info(
                        "Waiting %s seconds before looking for smartcard again",
                        SMARTCARD_RETRY_INTERVAL,
                    )
                    sleep(int(SMARTCARD_RETRY_INTERVAL))
            sleep(int(JOB_INTERVAL))


if __name__ == "__main__":
    main()
