from setuptools import setup, find_packages
from glob import glob

requires = [
        'grpcio==1.49.0',
        'pexpect==4.8.0',
        'protobuf==3.20.3',
        'python-gnupg==0.5.0',
        'yubikey-manager==4.0.8',
        'cython==3.0.0',
    ]

description = """Yubi-Bridge is a Python module that creates GPG keys for YubiKey and transfers them automatically to YubiKey. It can be run as a stand-alone application, or a client that takes jobs from DefGuard Core backend."""

setup(
    name='yubi-bridge',
    version='0.1.0',
    packages=find_packages(),
    tests_require=requires,
    install_requires=requires,
    description=description,
    long_description=description,
    entry_points={
        'console_scripts': [
            'yubi-bridge=yubi_bridge.main:main',
        ],
    },
    data_files=[
        ('/usr/share/yubi-bridge', ['yubi_bridge/main.py', 'yubi_bridge/client.py',  'yubi_bridge/__init__.py']),
        ('/usr/share/yubi-bridge/worker', glob('yubi-bridge/worker/*')),
    ],
)
