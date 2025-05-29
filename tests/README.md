# RemoteHost Utility and Testing

The `RemoteHost` utility (`src/remote_host.py`) provides a standardized way to interact with remote hosts over SSH, primarily for file transfer operations. It is accompanied by a suite of unit and integration tests.

## Overview

The `RemoteHost` class encapsulates SSH connection logic using the `netmiko` library. Its main purposes are:
*   Establishing and managing SSH connections using password or key-based authentication.
*   Providing methods for file downloads and uploads (currently placeholders, to be implemented with SCP/SFTP).
*   Handling connection errors gracefully.

## Setup for Testing

Testing for `RemoteHost` is divided into unit and integration tests. Integration tests require specific setup:

1.  **Configuration File (`tests/test_config.ini`)**:
    This file stores the necessary details for connecting to a remote server for integration testing. A sample structure is provided in `tests/test_config.ini`. You should copy this file (if it's not already present or if you need a custom version, e.g., `my_test_config.ini` and then point to it via CLI options if necessary, though the default is `tests/test_config.ini`) and **fill in your actual remote server details and desired file paths.**

    Example structure of `tests/test_config.ini`:
    ```ini
    [remote_test_server]
    # Replace placeholder values with your actual remote server details
    host = your_server_ip_or_hostname
    user = your_username
    password = your_password
    # ssh_key_path = /path/to/your/ssh/key # Uncomment if using key-based auth

    [test_files]
    # Define paths for local and remote files
    local_test_file_to_upload = tests/local_test_upload.txt
    remote_path_for_upload = /tmp/remote_test_upload.txt
    remote_test_file_to_download = /tmp/remote_test_download.txt
    local_path_for_download = /tmp/local_test_download.txt
    existing_remote_file_for_backup = /tmp/existing_remote_file.txt
    ```
    **Important**: Ensure the specified user has appropriate permissions on the remote server for the paths defined (e.g., read/write access to `/tmp/`).

2.  **Local Test File (`tests/local_test_upload.txt`)**:
    This file is used by integration tests for upload operations. It's a simple text file with sample content, located within the `tests/` directory.

## Running Unit Tests

Unit tests for `RemoteHost` are located in `tests/unit/test_remote_host.py`. They use mocking extensively to simulate SSH connections and do **not** require a live remote server or any specific configuration in `test_config.ini`.

To run all unit tests:
```bash
pytest tests/unit
```

## Running Integration Tests

Integration tests are located in `tests/integration/test_remote_host.py`. These tests **require a live, accessible remote server** and a correctly configured `tests/test_config.ini` file (or equivalent command-line overrides).

To run all integration tests:
```bash
pytest tests/integration
```

You can also use the `-s` flag with pytest to see `print` statements from the tests (e.g., connection status messages from `RemoteHost`):
```bash
pytest -s tests/integration
```

**Overriding Configuration with Command-Line Arguments**:
For flexibility, especially in CI/CD environments or for quick tests, you can override values from `test_config.ini` using command-line arguments when running `pytest`.

Available command-line options for integration tests:
*   `--ihost`: Remote host IP or hostname.
*   `--iuser`: Username for the remote host.
*   `--ipassword`: Password for the remote host.
*   `--ikeyfile`: Path to your SSH private key file.
*   `--iremote-file-dl`: Remote file path for download tests.
*   `--ilocal-file-dl`: Local path to save downloaded files.
*   `--ilocal-file-ul`: Local file path for upload tests.
*   `--iremote-file-ul`: Remote path to upload files to.
*   `--iexisting-remote-file-bkp`: Path to an existing remote file for backup tests.

Example of running integration tests with command-line overrides:
```bash
pytest tests/integration -s --ihost your.server.ip --iuser testuser --ipassword testpass --iremote-file-dl /remote/path/yourfile.txt --ilocal-file-dl /local/path/downloaded_yourfile.txt
```
If `--ipassword` is provided, it will be used for authentication. If `--ikeyfile` is provided, key-based authentication will be attempted. If both are provided via command line, the behavior might depend on the order of processing or specific `RemoteHost` logic (typically one should be chosen). The `RemoteHost` class itself expects either a password or a key file, but not both. The test configuration loader in `conftest.py` will prioritize CLI arguments: if you provide `--ipassword`, any `ssh_key_path` from the config file will be ignored, and vice-versa.
