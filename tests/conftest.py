import pytest
import configparser
import os

# Configuration file path - relative to the tests directory
CONFIG_FILE = "test_config.ini" # Assuming conftest.py is in tests/

def pytest_addoption(parser):
    """Adds command-line options for integration tests."""
    group = parser.getgroup("integration_tests", "Integration Test Options")
    group.addoption("--ihost", action="store", default=None, help="Remote host IP/hostname for integration tests")
    group.addoption("--iuser", action="store", default=None, help="Remote user for integration tests")
    group.addoption("--ipassword", action="store", default=None, help="Remote password for integration tests")
    group.addoption("--ikeyfile", action="store", default=None, help="Path to SSH key file for integration tests")
    
    group.addoption("--iremote-file-dl", action="store", default=None, help="Remote file path to download")
    group.addoption("--ilocal-file-dl", action="store", default=None, help="Local file path to save downloaded file")
    
    group.addoption("--ilocal-file-ul", action="store", default=None, help="Local file path to upload")
    group.addoption("--iremote-file-ul", action="store", default=None, help="Remote file path to upload to")
    
    group.addoption("--iexisting-remote-file-bkp", action="store", default=None, help="Existing remote file for backup test")

@pytest.fixture(scope="session")
def config(request):
    """
    Pytest fixture to read test configuration from file and command-line options.
    Command-line options override file configurations.
    """
    # Determine the absolute path to the config file, assuming conftest.py is in tests/
    base_dir = os.path.dirname(__file__) 
    config_file_path = os.path.join(base_dir, CONFIG_FILE)

    parser = configparser.ConfigParser()

    if not os.path.exists(config_file_path):
        # If config file doesn't exist, create an empty parser and rely on CLI or defaults
        # This path might be hit if tests are run from a context where test_config.ini isn't found
        # However, the original fixture skipped if not found. We'll try to build a config
        # primarily from CLI if the file is missing, or let it fail if essential CLI args are also missing.
        print(f"Warning: Configuration file {config_file_path} not found. "
              "Relying on command-line arguments or defaults.")
    else:
        try:
            parser.read(config_file_path)
        except configparser.Error as e:
            pytest.skip(f"Error parsing configuration file {config_file_path}: {e}. Skipping integration tests.")

    # Ensure sections exist, even if the file was not read or was empty
    if 'remote_test_server' not in parser:
        parser['remote_test_server'] = {}
    if 'test_files' not in parser:
        parser['test_files'] = {}

    # Override with command-line arguments if provided
    cli_host = request.config.getoption("--ihost")
    if cli_host is not None:
        parser['remote_test_server']['host'] = cli_host

    cli_user = request.config.getoption("--iuser")
    if cli_user is not None:
        parser['remote_test_server']['user'] = cli_user

    cli_password = request.config.getoption("--ipassword")
    if cli_password is not None:
        parser['remote_test_server']['password'] = cli_password
        if 'ssh_key_path' in parser['remote_test_server'] and cli_password:
             # If password is provided via CLI, it takes precedence, remove key path if it exists
             del parser['remote_test_server']['ssh_key_path']


    cli_keyfile = request.config.getoption("--ikeyfile")
    if cli_keyfile is not None:
        parser['remote_test_server']['ssh_key_path'] = cli_keyfile
        if 'password' in parser['remote_test_server'] and cli_keyfile:
            # If keyfile is provided via CLI, it takes precedence, remove password if it exists
            del parser['remote_test_server']['password']
            
    # If neither password nor keyfile is provided via CLI, and one was via config, ensure the other is cleared
    # This is to maintain the "password OR keyfile" logic if CLI changes one part.
    # However, RemoteHost itself will validate this, so just ensuring CLI options are set is primary.
    # If, for instance, config had a password, and CLI provides a keyfile, the password should be unset.
    # The above cli_password and cli_keyfile blocks already handle unsetting the other if one is provided.

    # Update test_files from CLI
    cli_remote_file_dl = request.config.getoption("--iremote-file-dl")
    if cli_remote_file_dl is not None:
        parser['test_files']['remote_test_file_to_download'] = cli_remote_file_dl

    cli_local_file_dl = request.config.getoption("--ilocal-file-dl")
    if cli_local_file_dl is not None:
        parser['test_files']['local_path_for_download'] = cli_local_file_dl

    cli_local_file_ul = request.config.getoption("--ilocal-file-ul")
    if cli_local_file_ul is not None:
        parser['test_files']['local_test_file_to_upload'] = cli_local_file_ul

    cli_remote_file_ul = request.config.getoption("--iremote-file-ul")
    if cli_remote_file_ul is not None:
        parser['test_files']['remote_path_for_upload'] = cli_remote_file_ul
        
    cli_existing_remote_file_bkp = request.config.getoption("--iexisting-remote-file-bkp")
    if cli_existing_remote_file_bkp is not None:
        parser['test_files']['existing_remote_file_for_backup'] = cli_existing_remote_file_bkp

    # Basic validation for essential parameters after merge
    # The remote_host_instance fixture will perform more detailed checks
    if not parser['remote_test_server'].get('host') or not parser['remote_test_server'].get('user'):
        pytest.skip("Essential connection parameters (host, user) missing after config load and CLI merge. Skipping integration tests.")

    return parser
