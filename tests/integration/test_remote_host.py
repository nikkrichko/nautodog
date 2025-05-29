import pytest
import configparser
import os
from datetime import datetime

from src.remote_host import RemoteHost, RemoteHostConnectionError

# Configuration file path
# CONFIG_FILE = "tests/test_config.ini" # Now handled by config fixture in conftest.py

# The 'config' fixture is now defined in tests/conftest.py
# and is session-scoped. It handles merging tests/test_config.ini
# with command-line arguments.

@pytest.fixture
def remote_host_instance(config):
    """
    Pytest fixture to create and manage a RemoteHost instance for tests.
    Skips tests if the remote server is unavailable or misconfigured.
    """
    server_config = config['remote_test_server']
    host = server_config.get('host')
    user = server_config.get('user')
    password = server_config.get('password', None)
    ssh_key_path = server_config.get('ssh_key_path', None)

    if not host or not user:
        pytest.skip("Host or user not specified in [remote_test_server] section of config. Skipping.")

    # Validate that either password or ssh_key_path is provided, but not both
    if not ((password is None) ^ (ssh_key_path is None)):
        # Check if they are effectively None or empty strings
        password_present = password and password.strip()
        key_present = ssh_key_path and ssh_key_path.strip()

        if not (password_present ^ key_present):
             pytest.skip(
                "Either password or ssh_key_path must be provided in [remote_test_server], "
                "but not both. Skipping."
            )
        if not password_present: password = None
        if not key_present: ssh_key_path = None


    rh_instance = None
    try:
        rh_instance = RemoteHost(
            host=host,
            user=user,
            password=password,
            ssh_key_path=ssh_key_path
        )
        # The RemoteHost constructor now calls check_connection, so this is implicitly tested.
        # If check_connection fails, it will raise RemoteHostConnectionError.
        yield rh_instance
    except RemoteHostConnectionError as e:
        pytest.skip(f"Failed to connect to remote server {host} as {user}: {e}. "
                    "Ensure server is available and config is correct. Skipping tests.")
    except ValueError as e: # Catch ValueError from RemoteHost __init__
        pytest.skip(f"Configuration error for RemoteHost: {e}. Skipping tests.")
    finally:
        if rh_instance and rh_instance._connection:
            rh_instance.close_connection()

def test_successful_connection(remote_host_instance):
    """
    Tests that a RemoteHost instance can be successfully created and connected.
    The fixture 'remote_host_instance' handles the connection check.
    """
    assert remote_host_instance is not None, "RemoteHost instance should be created if connection succeeds."
    try:
        # Ensure connection is usable for subsequent send_command calls in tests
        remote_host_instance.create_connection()
        assert remote_host_instance._connection.is_alive(), "Connection should be active for tests."
    except RemoteHostConnectionError as e:
        pytest.fail(f"check_connection failed after initial setup: {e}")
    finally:
        remote_host_instance.close_connection() # Close after check, tests will reopen


def remote_command(rh_instance, command, expect_string=None):
    """Helper function to execute a command on the remote host."""
    try:
        rh_instance.create_connection()
        # print(f"Executing remote command: {command}")
        output = rh_instance._connection.send_command(
            command, 
            strip_prompt=True, 
            strip_command=True,
            expect_string=expect_string
        )
        # print(f"Remote command output: {output}")
        return output
    finally:
        rh_instance.close_connection()

def remote_file_exists(rh_instance, remote_path):
    """Helper to check if a remote file exists."""
    return "EXISTS" in remote_command(rh_instance, f"sudo test -f {remote_path} && echo EXISTS || echo NOT_EXISTS")

def get_remote_file_content(rh_instance, remote_path):
    """Helper to get remote file content using sudo cat."""
    content = remote_command(rh_instance, f"sudo cat {remote_path}")
    # Sudo cat might return error messages if file doesn't exist or no permission
    if "No such file or directory" in content or "cannot open" in content:
        raise FileNotFoundError(f"Error getting content from {remote_path}: {content}")
    return content

@pytest.fixture
def remote_test_environment(remote_host_instance, config):
    """Fixture to manage remote test directory creation and cleanup."""
    base_dir = config.get('test_files', 'remote_dir_for_tests')
    remote_command(remote_host_instance, f"mkdir -p {base_dir}")
    remote_command(remote_host_instance, f"sudo chmod 777 {base_dir}") # Make it writable for tests
    yield base_dir # Provide the base directory to tests
    # Cleanup
    remote_command(remote_host_instance, f"sudo rm -rf {base_dir}")


def test_download_file(remote_host_instance, config, tmp_path, remote_test_environment):
    """Tests downloading a file from the remote host."""
    file_config = config['test_files']
    remote_base_dir = remote_test_environment # From fixture
    
    remote_source_filename = os.path.basename(file_config.get('remote_test_file_to_download'))
    remote_source_file = os.path.join(remote_base_dir, remote_source_filename)
    
    local_target_filename = file_config.get('local_path_for_download') # Just the filename
    local_target_file = tmp_path / local_target_filename
    
    test_content = file_config.get('test_content')

    # Setup: Create remote file
    remote_command(remote_host_instance, f"echo '{test_content}' | sudo tee {remote_source_file} > /dev/null")
    assert remote_file_exists(remote_host_instance, remote_source_file), f"Remote file {remote_source_file} was not created."

    # Execution
    downloaded_path = remote_host_instance.download_file(remote_source_file, str(local_target_file))

    # Verification
    assert downloaded_path == str(local_target_file), "Downloaded path does not match expected local target path."
    assert local_target_file.exists(), f"Local file {local_target_file} was not downloaded."
    assert local_target_file.read_text().strip() == test_content.strip(), "Content of downloaded file does not match expected."

    # Cleanup (local tmp_path is auto-cleaned by pytest, remote by remote_test_environment fixture)


def test_upload_file_new(remote_host_instance, config, tmp_path, remote_test_environment):
    """Tests uploading a new file to a remote host."""
    file_config = config['test_files']
    remote_base_dir = remote_test_environment

    # Setup local source file
    local_source_content = file_config.get('test_content')
    local_source_file = tmp_path / "upload_source.txt"
    local_source_file.write_text(local_source_content)

    remote_target_filename = os.path.basename(file_config.get('remote_path_for_upload'))
    remote_target_file = os.path.join(remote_base_dir, remote_target_filename)

    # Ensure remote target file does not exist initially (covered by remote_test_environment cleanup)
    if remote_file_exists(remote_host_instance, remote_target_file):
         remote_command(remote_host_instance, f"sudo rm -f {remote_target_file}")
    assert not remote_file_exists(remote_host_instance, remote_target_file), f"Remote file {remote_target_file} exists before test."


    # Execution
    remote_host_instance.upload_file(str(local_source_file), remote_target_file)

    # Verification
    assert remote_file_exists(remote_host_instance, remote_target_file), f"Remote file {remote_target_file} was not uploaded."
    
    uploaded_content = get_remote_file_content(remote_host_instance, remote_target_file)
    assert uploaded_content.strip() == local_source_content.strip(), "Content of uploaded file does not match expected."

    # Cleanup (local tmp_path is auto-cleaned, remote by remote_test_environment fixture)


def test_upload_file_with_backup(remote_host_instance, config, tmp_path, remote_test_environment):
    """Tests uploading a file that replaces an existing file, checking for backup."""
    file_config = config['test_files']
    remote_base_dir = remote_test_environment

    original_content = file_config.get('original_backup_content')
    new_content = file_config.get('new_upload_content')

    # Setup local source file with new content
    local_source_file_new = tmp_path / "upload_source_new.txt"
    local_source_file_new.write_text(new_content)

    remote_target_filename = os.path.basename(file_config.get('existing_remote_file_for_backup'))
    remote_target_file_for_backup = os.path.join(remote_base_dir, remote_target_filename)
    
    # Create original remote file
    remote_command(remote_host_instance, f"echo '{original_content}' | sudo tee {remote_target_file_for_backup} > /dev/null")
    assert remote_file_exists(remote_host_instance, remote_target_file_for_backup), f"Original remote file {remote_target_file_for_backup} was not created."

    # Execution
    remote_host_instance.upload_file(str(local_source_file_new), remote_target_file_for_backup)

    # Verification: Target file content
    assert remote_file_exists(remote_host_instance, remote_target_file_for_backup), f"Target remote file {remote_target_file_for_backup} does not exist after upload."
    uploaded_content = get_remote_file_content(remote_host_instance, remote_target_file_for_backup)
    assert uploaded_content.strip() == new_content.strip(), "Content of target file after upload is not the new content."

    # Verification: Backup file
    backup_dir_path = os.path.join(os.path.dirname(remote_target_file_for_backup), "backup_files")
    
    # List files in backup directory
    # The command `ls -1 {backup_dir_path}` should give one filename per line.
    # We expect one file matching the pattern.
    ls_output = remote_command(remote_host_instance, f"sudo ls -A1 {backup_dir_path}") # -A to list almost all, -1 for one per line
    
    # Construct expected backup filename pattern (filename_YYYYMMDDHHMMSS)
    expected_backup_pattern = f"{remote_target_filename}_" # Timestamp is variable
    
    backup_files_found = [f for f in ls_output.splitlines() if f.startswith(expected_backup_pattern)]
    
    assert len(backup_files_found) >= 1, f"No backup file found for {remote_target_filename} in {backup_dir_path}. ls output: '{ls_output}'"
    
    # Assuming the first match is our backup file (could be more robust if multiple backups are possible)
    # For this test, we assume only one relevant backup operation.
    backup_file_name = backup_files_found[0]
    full_backup_path = os.path.join(backup_dir_path, backup_file_name)
    
    assert remote_file_exists(remote_host_instance, full_backup_path), f"Backup file {full_backup_path} does not exist."
    
    backup_content = get_remote_file_content(remote_host_instance, full_backup_path)
    assert backup_content.strip() == original_content.strip(), "Content of backup file does not match original content."

    # Cleanup (local tmp_path is auto-cleaned, remote by remote_test_environment fixture)

# Example of how to run (from the project root directory):
# python -m pytest tests/integration/test_remote_host.py -s
#
# Remember to:
# 1. Install pytest: pip install pytest netmiko
# 2. Create/update tests/test_config.ini with valid remote server details.
# 3. Ensure the specified local_test_file_to_upload exists (e.g., tests/local_test_upload.txt)
# 4. Ensure the remote server is accessible and the user has permissions for /tmp/ (or configured paths).
# 5. For download tests, ensure remote_test_file_to_download exists on the server.
#    (e.g., by manually placing /tmp/remote_test_download.txt on the server)
#
# If the server is not available or config is wrong, tests relying on remote_host_instance
# should be skipped automatically by the fixture.
# The test_successful_connection will only pass if a connection can be made.
# The placeholder tests will "pass" by asserting True if the connection is made.
#
# The RemoteHost class uses device_type='linux'.
# The tests assume this and will use it when instantiating RemoteHost.
#
# The `remote_host_instance` fixture handles skipping tests if the remote server
# isn't available based on the `check_connection()` result in `RemoteHost.__init__()`.
# If `RemoteHost.__init__()` raises `RemoteHostConnectionError`, the fixture catches it
# and calls `pytest.skip()`.
#
# The `os` and `datetime` imports are included as they might be needed for future
# enhancements to these tests, such as creating unique filenames or checking timestamps.
# For now, `os` is used for `os.path.exists` and `os.makedirs`.
# `datetime` is not actively used in this version but is good to have for potential future use.

# Make sure __init__.py exists in tests and tests/integration if running pytest module-wise
# For example, create empty files:
# tests/__init__.py
# tests/integration/__init__.py
# src/__init__.py (if not already present)
# This helps pytest discover modules and packages correctly.
#
# The project structure assumed:
# project_root/
#  src/
#    __init__.py
#    remote_host.py
#  tests/
#    __init__.py
#    test_config.ini
#    local_test_upload.txt
#    integration/
#      __init__.py
#      test_remote_host.py
#  pytest.ini (optional, for pytest configuration)
#
# To run all tests: pytest
# To run specific integration tests: pytest tests/integration/
# To run a specific test file: pytest tests/integration/test_remote_host.py
# To run with verbose output and print statements: pytest -s tests/integration/test_remote_host.py
#
# The `RemoteHost` class's `__init__` method calls `check_connection`, which attempts
# to connect and then disconnects. This means the `remote_host_instance` fixture
# will cause a connection attempt. If it fails, `pytest.skip` is called.
# The placeholder file transfer methods in `RemoteHost` also create and close
# connections for their operations.
#
# The `config` fixture has `scope="session"` because the config file is unlikely to change
# during a test session. The `remote_host_instance` fixture has default scope ("function"),
# meaning a new `RemoteHost` instance (and thus a new connection attempt via its __init__)
# will be made for each test function that uses it. This ensures test isolation.
#
# Added basic validation in `config` fixture for `CONFIG_FILE` existence and
# `[remote_test_server]` section.
# Added validation in `remote_host_instance` for host/user presence and
# password/ssh_key_path exclusivity.
# Added `os.makedirs` in `test_download_file_placeholder` to ensure local download directory exists.
# Added check for `local_test_file_to_upload` existence in `test_upload_file_placeholder`.
# The `test_successful_connection` was also slightly enhanced to call `check_connection` again
# to be absolutely sure, though `RemoteHost.__init__` already does this.
# The `remote_host_instance` fixture now also catches `ValueError` from `RemoteHost.__init__`
# for cases where password/key are misconfigured.
#
# Note: The actual file transfer operations within `download_file` and `upload_file`
# in `RemoteHost` are currently placeholders. These tests will pass if the connection
# to the remote host is successful, as the placeholder methods just print messages
# after connecting. The actual file transfer logic and more detailed assertions
# will be part of a future task.
#
# The `remote_host_instance` fixture will yield the `RemoteHost` instance and
# then, in its teardown phase (after `yield`), it explicitly calls `close_connection()`
# if the instance and its connection exist. This is good practice for fixtures
# that manage resources, although `RemoteHost` methods are designed to manage their
# own connections. This ensures that even if a test fails mid-execution after the
# `RemoteHost` object is created, the connection is attempted to be closed.
#
# The `device_type='linux'` is hardcoded in `RemoteHost` and does not need to be
# specified again in the tests when creating `RemoteHost` instance, as the class
# handles this internally.
#
# Final structure of this file:
# - Imports
# - CONFIG_FILE constant
# - `config` fixture
# - `remote_host_instance` fixture
# - `test_successful_connection`
# - `test_download_file_placeholder`
# - `test_upload_file_placeholder`
# - Comments with instructions and explanations.
