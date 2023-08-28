from tempfile import TemporaryDirectory

import pytest

from main import YubiBridge
from tests import fixtures


# Succes write to yubikey
@pytest.fixture
def mock_write_to_yubikey(mocker):
    mocker.patch("YubiBridge.write_to_yubikey", return_value=None)


@pytest.fixture
def mock_write_to_yubikey_error(mocker):
    mocker.patch("YubiBridge.write_to_yubikey", return_value=SystemExit)


@pytest.fixture
def mock_create_keys(mocker):
    mocker.patch("YubiBridge.create_keypair", return_value="FINGERPRINT")


@pytest.fixture
def mock_yubikey_success(mocker):
    mocker.patch("YubiBridge.check_yk", return_value=True)


@pytest.fixture
def mock_nodevices(mocker):
    mocker.patch("ykman.device.list_all_devices", return_value=[])


@pytest.fixture
def mock_pubkeys(mocker):
    mocker.patch("gnupg.GPG.list_keys", return_value=fixtures.list_keys)
    mocker.patch("gnupg.GPG.export_keys", return_value=fixtures.public_key_asc)


def test_create_keys():
    with TemporaryDirectory() as tempdir:
        yb = YubiBridge(tempdir)
        assert yb.create_keypair("marek test", "test@o2.pl")
