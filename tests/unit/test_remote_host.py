import pytest
from unittest.mock import patch, MagicMock

from src.remote_host import RemoteHost, RemoteHostConnectionError
# Assuming netmiko exceptions are importable for type checking if needed,
# but for mocking, we primarily care about their names as strings or the exceptions themselves.
from netmiko.ssh_exception import NetmikoTimeoutException, NetmikoAuthenticationException

class TestRemoteHostInitialization:
    """Tests for RemoteHost.__init__ and its internal call to check_connection."""

    @patch('src.remote_host.ConnectHandler')
    def test_init_with_password_success(self, mock_connect_handler):
        """Test successful initialization with password and connection check."""
        mock_conn_instance = MagicMock()
        mock_connect_handler.return_value = mock_conn_instance

        rh = RemoteHost(host="test_host", user="test_user", password="test_password")

        mock_connect_handler.assert_called_once_with(
            device_type="linux",
            host="test_host",
            username="test_user",
            password="test_password"
        )
        mock_conn_instance.disconnect.assert_called_once()
        assert rh.host == "test_host" # Check if attributes are set

    @patch('src.remote_host.ConnectHandler')
    def test_init_with_ssh_key_success(self, mock_connect_handler):
        """Test successful initialization with SSH key and connection check."""
        mock_conn_instance = MagicMock()
        mock_connect_handler.return_value = mock_conn_instance

        rh = RemoteHost(host="test_host", user="test_user", ssh_key_path="/path/to/key")

        mock_connect_handler.assert_called_once_with(
            device_type="linux",
            host="test_host",
            username="test_user",
            key_file="/path/to/key"
        )
        mock_conn_instance.disconnect.assert_called_once()
        assert rh.ssh_key_path == "/path/to/key"

    def test_init_missing_credentials(self):
        """Test ValueError if neither password nor SSH key is provided."""
        with pytest.raises(ValueError, match="Either password or ssh_key_path must be provided"):
            RemoteHost(host="test_host", user="test_user")

    def test_init_both_credentials(self):
        """Test ValueError if both password and SSH key are provided."""
        with pytest.raises(ValueError, match="Either password or ssh_key_path must be provided"):
            RemoteHost(host="test_host", user="test_user", password="pwd", ssh_key_path="/key")

    @patch('src.remote_host.ConnectHandler', side_effect=NetmikoAuthenticationException("Auth failed"))
    def test_init_connection_authentication_failure(self, mock_connect_handler):
        """Test RemoteHostConnectionError on NetmikoAuthenticationException during init."""
        with pytest.raises(RemoteHostConnectionError, match="Failed to connect to test_host: Auth failed"):
            RemoteHost(host="test_host", user="test_user", password="test_password")
        mock_connect_handler.assert_called_once() # Ensure it was attempted

    @patch('src.remote_host.ConnectHandler', side_effect=NetmikoTimeoutException("Timeout"))
    def test_init_connection_timeout_failure(self, mock_connect_handler):
        """Test RemoteHostConnectionError on NetmikoTimeoutException during init."""
        with pytest.raises(RemoteHostConnectionError, match="Failed to connect to test_host: Timeout"):
            RemoteHost(host="test_host", user="test_user", password="test_password")
        mock_connect_handler.assert_called_once()


class TestRemoteHostConnectionManagement:
    """Tests for create_connection and close_connection methods."""

    @patch('src.remote_host.ConnectHandler')
    @patch.object(RemoteHost, 'check_connection', return_value=None) # Bypass __init__'s check
    def test_create_connection_success(self, mock_check_conn, mock_connect_handler):
        """Test creating a new connection."""
        mock_conn_instance = MagicMock()
        mock_conn_instance.is_alive.return_value = True
        mock_connect_handler.return_value = mock_conn_instance

        rh = RemoteHost(host="test_host", user="test_user", password="pwd")
        rh._connection = None # Ensure no connection initially

        rh.create_connection()
        mock_connect_handler.assert_called_once_with(
            device_type="linux", host="test_host", username="test_user", password="pwd"
        )
        assert rh._connection == mock_conn_instance

        # Call again, should not create a new connection if old one is alive
        rh.create_connection()
        mock_connect_handler.assert_called_once() # Still called only once

    @patch('src.remote_host.ConnectHandler')
    @patch.object(RemoteHost, 'check_connection', return_value=None)
    def test_create_connection_when_connection_dead(self, mock_check_conn, mock_connect_handler):
        """Test creating a new connection if the existing one is dead."""
        mock_conn_instance_initial = MagicMock()
        mock_conn_instance_initial.is_alive.return_value = False # Simulate dead connection
        
        mock_conn_instance_new = MagicMock()
        mock_conn_instance_new.is_alive.return_value = True
        
        # Make ConnectHandler return the new mock on the second call
        mock_connect_handler.side_effect = [mock_conn_instance_initial, mock_conn_instance_new]

        rh = RemoteHost(host="test_host", user="test_user", password="pwd")
        rh._connection = mock_conn_instance_initial # Set an initial "dead" connection

        rh.create_connection() # First call, connection is dead, so should try to connect
        rh.create_connection() # Second call, should establish a new connection

        assert mock_connect_handler.call_count == 2
        assert rh._connection == mock_conn_instance_new


    @patch.object(RemoteHost, 'check_connection', return_value=None) # Bypass __init__'s check
    def test_close_connection_active(self, mock_check_conn):
        """Test closing an active connection."""
        rh = RemoteHost(host="test_host", user="test_user", password="pwd")
        
        mock_conn_instance = MagicMock()
        mock_conn_instance.is_alive.return_value = True
        rh._connection = mock_conn_instance # Manually set an active connection

        rh.close_connection()

        mock_conn_instance.disconnect.assert_called_once()
        assert rh._connection is None

    @patch.object(RemoteHost, 'check_connection', return_value=None)
    def test_close_connection_inactive(self, mock_check_conn):
        """Test closing when connection is already None or not alive."""
        rh = RemoteHost(host="test_host", user="test_user", password="pwd")
        
        # Case 1: Connection is already None
        rh._connection = None
        rh.close_connection() # Should not raise error

        # Case 2: Connection is not alive
        mock_conn_instance = MagicMock()
        mock_conn_instance.is_alive.return_value = False
        rh._connection = mock_conn_instance
        
        rh.close_connection()
        mock_conn_instance.disconnect.assert_not_called() # is_alive is false, so disconnect not called
        assert rh._connection is None


from unittest.mock import mock_open # For mocking open()

# Mock datetime for consistent timestamp generation in tests
FIXED_DATETIME = MagicMock()
FIXED_DATETIME.now.return_value.strftime.return_value = "20230101120000"


@patch('src.remote_host.datetime', FIXED_DATETIME) # Patch datetime globally for this module
class TestRemoteHostFileOperations:
    """Tests for download_file and upload_file methods of RemoteHost."""

    def _setup_rh_and_mocks(self, rh_init_bypass_check=True):
        """Helper to setup RemoteHost instance and common mocks."""
        if rh_init_bypass_check:
            # Bypass __init__'s check_connection for most unit tests
            patcher = patch.object(RemoteHost, 'check_connection', return_value=None)
            patcher.start()
            self.addCleanup(patcher.stop)

        rh = RemoteHost(host="test_host", user="test_user", password="pwd")
        
        # Mock the Netmiko connection object and its SFTP capabilities
        rh._connection = MagicMock() 
        mock_sftp_client = MagicMock()
        rh._connection.remote_conn.open_sftp.return_value = mock_sftp_client
        
        return rh, mock_sftp_client

    # --- Tests for download_file ---
    @patch('src.remote_host.os')
    def test_download_file_sftp_success(self, mock_os):
        """Test successful file download using SFTP."""
        rh, mock_sftp = self._setup_rh_and_mocks()

        mock_os.path.exists.return_value = True # Assume local dir exists or is root
        mock_os.path.abspath.side_effect = lambda x: f"/abs/{x}"
        mock_os.path.basename.side_effect = lambda x: x.split('/')[-1]
        mock_os.path.join.side_effect = os.path.join # Use real os.path.join

        rh._connection.send_command.return_value = "EXISTS_READABLE" # Mock file check

        local_path = rh.download_file("/remote/file.txt", "local/file.txt")

        rh._connection.send_command.assert_any_call("if [ -f '/remote/file.txt' ] && [ -r '/remote/file.txt' ]; then echo 'EXISTS_READABLE'; else echo 'NOT_FOUND_OR_UNREADABLE'; fi", strip_prompt=True, strip_command=True)
        mock_sftp.get.assert_called_once_with("/remote/file.txt", "/abs/local/file.txt")
        assert local_path == "/abs/local/file.txt"
        rh._connection.remote_conn.open_sftp.assert_called_once() # Ensure sftp client was opened
        mock_sftp.close.assert_called_once() # Ensure sftp client was closed
        rh.close_connection.assert_called_once() # Ensure main SSH conn was closed

    @patch('src.remote_host.os')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_file_sftp_fails_sudo_cat_success(self, mock_file_open, mock_os):
        """Test SFTP fail then sudo cat success for download."""
        rh, mock_sftp = self._setup_rh_and_mocks()

        mock_sftp.get.side_effect = Exception("SFTP failed")
        rh._connection.send_command.side_effect = [
            "EXISTS_READABLE",  # For file check
            "file content"      # For sudo cat
        ]
        mock_os.path.exists.return_value = True
        mock_os.path.abspath.side_effect = lambda x: f"/abs/{x}"
        mock_os.path.basename.side_effect = lambda x: x.split('/')[-1]
        mock_os.path.join.side_effect = os.path.join

        local_path = rh.download_file("/remote/file.txt", "local/file.txt")

        mock_sftp.get.assert_called_once()
        rh._connection.send_command.assert_any_call("sudo cat '/remote/file.txt'", strip_prompt=True, strip_command=True)
        mock_file_open.assert_called_once_with("/abs/local/file.txt", 'wb')
        mock_file_open().write.assert_called_once_with(b"file content")
        assert local_path == "/abs/local/file.txt"

    def test_download_file_remote_not_found(self):
        """Test download when remote file is not found."""
        rh, _ = self._setup_rh_and_mocks()
        rh._connection.send_command.return_value = "NOT_FOUND_OR_UNREADABLE"

        with pytest.raises(FileNotFoundError, match="Remote file /remote/file.txt does not exist"):
            rh.download_file("/remote/file.txt", "local/file.txt")

    @patch('src.remote_host.os')
    def test_download_file_sftp_and_sudo_cat_fail(self, mock_os):
        """Test download failure when both SFTP and sudo cat fail."""
        rh, mock_sftp = self._setup_rh_and_mocks()
        mock_sftp.get.side_effect = Exception("SFTP failed")
        rh._connection.send_command.side_effect = [
            "EXISTS_READABLE",  # File check
            Exception("sudo cat failed") # Sudo cat failure
        ]
        mock_os.path.exists.return_value = True
        mock_os.path.abspath.side_effect = lambda x: f"/abs/{x}"

        with pytest.raises(PermissionError, match="'sudo cat' download attempt for '/remote/file.txt' failed: Exception\\('sudo cat failed'\\)"):
            rh.download_file("/remote/file.txt", "local/file.txt")

    @patch('src.remote_host.os')
    def test_download_file_temp_local_path_generation(self, mock_os):
        """Test default local path generation for download."""
        rh, mock_sftp = self._setup_rh_and_mocks()

        rh._connection.send_command.return_value = "EXISTS_READABLE"
        # Simulate 'temp_downloads' directory does not exist initially, then created
        mock_os.path.exists.side_effect = [False, True] 
        mock_os.path.abspath.side_effect = lambda x: f"/abs/{x}" if x != "temp_downloads" else "/abs/temp_downloads"
        mock_os.path.basename.return_value = "file.txt"
        # Ensure os.path.join works as expected for constructing paths
        mock_os.path.join.side_effect = lambda *args: os.path.normpath("/".join(args))


        local_path = rh.download_file("/remote/file.txt") # local_file_path=None

        mock_os.makedirs.assert_any_call("temp_downloads") # Check if 'temp_downloads' was created
        mock_os.makedirs.assert_any_call(os.path.normpath("/abs/temp_downloads"), exist_ok=True) # Check if final path dir created
        
        # Expected path: abspath(join(project_root_temp_dir, local_file_name))
        # project_root_temp_dir = "temp_downloads"
        # local_file_name = os.path.basename("/remote/file.txt") -> "file.txt"
        # Expected: /abs/temp_downloads/file.txt
        assert local_path == os.path.normpath("/abs/temp_downloads/file.txt")
        mock_sftp.get.assert_called_once_with("/remote/file.txt", os.path.normpath("/abs/temp_downloads/file.txt"))


    # --- Tests for upload_file ---
    @patch('src.remote_host.os')
    def test_upload_file_new_file_success(self, mock_os):
        """Test successful upload of a new file."""
        rh, mock_sftp = self._setup_rh_and_mocks()

        mock_os.path.exists.return_value = True # Local file exists
        mock_os.path.dirname.return_value = "/remote/target_dir"
        mock_os.path.basename.return_value = "file.txt"
        
        # SFTP stat side effects:
        # 1. Remote target dir exists (or created successfully)
        # 2. Remote file does not exist (FileNotFoundError for backup check)
        mock_sftp.stat.side_effect = [True, FileNotFoundError] 

        rh.upload_file("/local/source.txt", "/remote/target_dir/file.txt")

        mock_sftp.put.assert_called_once_with("/local/source.txt", "/tmp/nautodog_uploads/20230101120000/file.txt")
        rh._connection.send_command.assert_any_call("sudo mv /tmp/nautodog_uploads/20230101120000/file.txt /remote/target_dir/file.txt", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("rm -rf /tmp/nautodog_uploads/20230101120000", strip_prompt=True, strip_command=True)
        # Ensure backup related commands were NOT called
        assert not any("cp " in call.args[0] for call in rh._connection.send_command.call_args_list if "stat -c" not in call.args[0] and "mkdir" not in call.args[0])
        rh._connection.remote_conn.open_sftp.assert_called_once()
        mock_sftp.close.assert_called_once()
        rh.close_connection.assert_called_once()


    @patch('src.remote_host.os')
    def test_upload_file_with_backup_success(self, mock_os):
        """Test successful upload with backup of existing file."""
        rh, mock_sftp = self._setup_rh_and_mocks()

        mock_os.path.exists.return_value = True # Local file exists
        mock_os.path.dirname.return_value = "/remote/target_dir"
        mock_os.path.basename.return_value = "file.txt"
        mock_os.path.join.side_effect = os.path.join # Use real join

        # SFTP stat: remote target dir exists, remote file exists (backup needed)
        mock_sftp.stat.side_effect = [True, True] 
        
        # send_command side effects:
        # 1. stat -c (ownership/perms) -> "user:group 755"
        # 2. mkdir -p backup_dir
        # 3. cp (backup) -> success (empty output)
        # 4. sudo chown (backup)
        # 5. sudo chmod (backup)
        # 6. mkdir -p temp_upload_base_dir
        # 7. mkdir -p temp_upload_timestamp_dir
        # 8. sudo mv (final move) -> success
        # 9. sudo chown (final file)
        # 10. sudo chmod (final file)
        # 11. rm -rf (cleanup)
        rh._connection.send_command.side_effect = [
            "user:group 755", "", "", "", "", "", "", "", "", "", "" 
        ]

        rh.upload_file("/local/source.txt", "/remote/target_dir/file.txt")

        mock_sftp.put.assert_called_once_with("/local/source.txt", "/tmp/nautodog_uploads/20230101120000/file.txt")
        
        # Check backup commands
        rh._connection.send_command.assert_any_call("stat -c '%U:%G %a' /remote/target_dir/file.txt", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("mkdir -p /remote/target_dir/backup_files", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("cp /remote/target_dir/file.txt /remote/target_dir/backup_files/file.txt_20230101120000", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("sudo chown user:group /remote/target_dir/backup_files/file.txt_20230101120000", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("sudo chmod 755 /remote/target_dir/backup_files/file.txt_20230101120000", strip_prompt=True, strip_command=True)
        
        # Check final move and permission commands
        rh._connection.send_command.assert_any_call("sudo mv /tmp/nautodog_uploads/20230101120000/file.txt /remote/target_dir/file.txt", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("sudo chown user:group /remote/target_dir/file.txt", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("sudo chmod 755 /remote/target_dir/file.txt", strip_prompt=True, strip_command=True)
        
        rh._connection.send_command.assert_any_call("rm -rf /tmp/nautodog_uploads/20230101120000", strip_prompt=True, strip_command=True)

    @patch('src.remote_host.os.path.exists', return_value=False)
    def test_upload_file_local_file_not_found(self, mock_exists):
        """Test upload when local file is not found."""
        rh, _ = self._setup_rh_and_mocks()
        with pytest.raises(FileNotFoundError, match="Local file /local/source.txt not found"):
            rh.upload_file("/local/source.txt", "/remote/file.txt")
        mock_exists.assert_called_once_with("/local/source.txt")

    @patch('src.remote_host.os')
    def test_upload_file_remote_dir_creation_failure(self, mock_os):
        """Test upload failure if remote target directory cannot be created."""
        rh, mock_sftp = self._setup_rh_and_mocks()
        mock_os.path.exists.return_value = True # Local file exists
        mock_os.path.dirname.return_value = "/remote/target_dir"

        # sftp.stat for remote target dir raises FileNotFoundError twice (before and after mkdir attempt)
        mock_sftp.stat.side_effect = FileNotFoundError 
        
        # Mock send_command for mkdir -p (it won't actually create it, sftp.stat will confirm failure)
        rh._connection.send_command.return_value = "" 

        with pytest.raises(PermissionError, match="Failed to create remote directory /remote/target_dir"):
            rh.upload_file("/local/source.txt", "/remote/target_dir/file.txt")
        
        rh._connection.send_command.assert_any_call("mkdir -p /remote/target_dir", strip_prompt=True, strip_command=True)


    @patch('src.remote_host.os')
    def test_upload_file_backup_cp_fails_sudo_cp_succeeds(self, mock_os):
        """Test backup uses sudo cp if direct cp fails."""
        rh, mock_sftp = self._setup_rh_and_mocks()
        mock_os.path.exists.return_value = True
        mock_os.path.dirname.return_value = "/remote/target_dir"
        mock_os.path.basename.return_value = "file.txt"
        mock_os.path.join.side_effect = os.path.join

        mock_sftp.stat.side_effect = [True, True] # Target dir and file exist

        rh._connection.send_command.side_effect = [
            "user:group 755",  # stat -c
            "",                 # mkdir -p backup_dir
            "cp: permission denied", # cp fails
            "",                 # sudo cp succeeds
            "", "", "", "", "", "", "" # other sudo chown, chmod, mkdir, mv, rm
        ]

        rh.upload_file("/local/source.txt", "/remote/target_dir/file.txt")

        rh._connection.send_command.assert_any_call("cp /remote/target_dir/file.txt /remote/target_dir/backup_files/file.txt_20230101120000", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("sudo cp /remote/target_dir/file.txt /remote/target_dir/backup_files/file.txt_20230101120000", strip_prompt=True, strip_command=True)


    @patch('src.remote_host.os')
    def test_upload_file_sudo_mv_fails(self, mock_os):
        """Test upload failure if sudo mv fails."""
        rh, mock_sftp = self._setup_rh_and_mocks()
        mock_os.path.exists.return_value = True
        mock_os.path.dirname.return_value = "/remote/target_dir"
        mock_os.path.basename.return_value = "file.txt"

        mock_sftp.stat.side_effect = [True, FileNotFoundError] # Target dir exists, file does not (no backup)
        mock_sftp.put.return_value = None # SFTP upload to temp succeeds

        rh._connection.send_command.side_effect = [
            "", # mkdir -p target (if sftp.stat for dir failed, but here it passes)
            "", # mkdir -p temp_base
            "", # mkdir -p temp_ts
            "mv: permission denied", # sudo mv fails
            "NOT_EXISTS" # sudo test -f confirms mv failed
        ]

        with pytest.raises(PermissionError, match="Failed to move file from /tmp/nautodog_uploads/20230101120000/file.txt to /remote/target_dir/file.txt using sudo. Error: mv: permission denied. Target check: NOT_EXISTS"):
            rh.upload_file("/local/source.txt", "/remote/target_dir/file.txt")
        
        mock_sftp.put.assert_called_once()
        rh._connection.send_command.assert_any_call("sudo mv /tmp/nautodog_uploads/20230101120000/file.txt /remote/target_dir/file.txt", strip_prompt=True, strip_command=True)
        rh._connection.send_command.assert_any_call("sudo test -f /remote/target_dir/file.txt && echo EXISTS || echo NOT_EXISTS", strip_prompt=True, strip_command=True)


# Example of how to run these tests with pytest:
# pytest tests/unit/test_remote_host.py::TestRemoteHostFileOperations
#
# To run a specific test class:
# pytest tests/unit/test_remote_host.py::TestRemoteHostInitialization
#
# To run a specific test function:
# pytest tests/unit/test_remote_host.py::TestRemoteHostInitialization::test_init_with_password_success
#
# Remember to have __init__.py files in src/ and tests/unit/ for pytest discovery if needed.
# project_root/
#  src/
#    __init__.py
#    remote_host.py
#  tests/
#    __init__.py
#    unit/
#      __init__.py
#      test_remote_host.py
#
# These tests mock out the actual netmiko.ConnectHandler, so they don't require a live SSH server.
# They focus on the logic within the RemoteHost class itself.
#
# The use of @patch.object(RemoteHost, 'check_connection', return_value=None)
# is to prevent the actual check_connection logic (which involves ConnectHandler)
# from running during the __init__ phase of tests that are not specifically
# testing check_connection itself. This isolates the unit being tested.
#
# For tests in TestRemoteHostInitialization that *do* test check_connection implicitly,
# we patch ConnectHandler directly and let check_connection run.
#
# Added test_create_connection_when_connection_dead to cover the case where an existing
# connection is not alive.
# Modified test_close_connection_inactive to ensure disconnect is not called if
# the connection is not alive, as per the current implementation of RemoteHost.close_connection.
# Added test_download_file_local_path_generation to check the default local path logic.
