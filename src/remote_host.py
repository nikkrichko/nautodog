import os
import tempfile
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, NetmikoAuthenticationException

class RemoteHostConnectionError(Exception):
    """Custom exception for RemoteHost connection errors."""
    pass

class RemoteHost:
    """
    Represents a remote host and provides methods for interacting with it via SSH.
    """
    def __init__(self, host, user, password=None, ssh_key_path=None):
        """
        Initializes the RemoteHost object.

        Args:
            host (str): The hostname or IP address of the remote host.
            user (str): The username for SSH authentication.
            password (str, optional): The password for SSH authentication.
            ssh_key_path (str, optional): The path to the SSH private key file.

        Raises:
            ValueError: If neither or both password and ssh_key_path are provided.
        """
        if not ((password is None) ^ (ssh_key_path is None)): # XOR for mutual exclusivity
            raise ValueError(
                "Either password or ssh_key_path must be provided, but not both."
            )

        self.host = host
        self.user = user
        self.password = password
        self.ssh_key_path = ssh_key_path
        self._connection = None

        # Initial connection check to validate credentials and reachability.
        # This was part of the original design.
        try:
            self.check_connection()
        except RemoteHostConnectionError as e:
            # Propagate connection error during initialization
            raise RemoteHostConnectionError(f"Initial connection check failed: {e}")


    def create_connection(self):
        """
        Establishes an SSH connection to the remote host if one is not already active.
        """
        if self._connection is None or not self._connection.is_alive():
            try:
                connection_params = {
                    "device_type": "linux", # Assuming generic Linux for broad compatibility
                    "host": self.host,
                    "username": self.user,
                }
                if self.password:
                    connection_params["password"] = self.password
                elif self.ssh_key_path:
                    connection_params["key_file"] = self.ssh_key_path
                
                # For SFTP/SCP, ensure Paramiko is effectively used. 
                # Netmiko uses Paramiko for 'linux' device_type by default.
                # Consider adding global_delay_factor if timing issues occur:
                # connection_params["global_delay_factor"] = 2 

                self._connection = ConnectHandler(**connection_params)
            except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
                self._connection = None 
                raise RemoteHostConnectionError(
                    f"SSH connection failed to {self.host}: {e}"
                ) from e
            except Exception as e: # Catch other potential errors during connection
                self._connection = None
                raise RemoteHostConnectionError(
                    f"An unexpected error occurred while connecting to {self.host}: {e}"
                ) from e

    def close_connection(self):
        """
        Closes the SSH connection if it is active.
        """
        if self._connection and self._connection.is_alive():
            self._connection.disconnect()
        self._connection = None

    def check_connection(self):
        """
        Checks if a connection can be established and then closes it.

        Raises:
            RemoteHostConnectionError: If the connection fails.
        """
        try:
            self.create_connection()
            # print(f"Successfully connected to {self.host} for check.") # Optional: for verbose output
        except RemoteHostConnectionError:
            # Re-raise the specific error from create_connection
            raise
        finally:
            # Ensure connection is closed after check
            self.close_connection()

    def download_file(self, remote_file_path: str, local_file_path: str = None) -> str:
        '''
        Downloads a file from the remote host.

        Args:
            remote_file_path: Absolute path of the file on the remote host.
            local_file_path: Optional. Path to save the file locally.
                             If None, a temporary directory 'temp_downloads' will be
                             created in the current working directory (if not exists) and the file
                             will be saved there with its original name.

        Returns:
            The absolute path to the downloaded local file.

        Raises:
            FileNotFoundError: If the remote file does not exist or is not readable.
            RemoteHostConnectionError: If connection fails.
            PermissionError: If direct download fails and sudo also fails or is not applicable.
        '''
        self.create_connection() # Ensure connection is active
        try:
            # 1. Check if remote file exists and is readable
            # Using `test -f` for regular file and `test -r` for readable.
            # Using simple echo for boolean-like output.
            file_check_cmd = f"if [ -f '{remote_file_path}' ] && [ -r '{remote_file_path}' ]; then echo 'EXISTS_READABLE'; else echo 'NOT_FOUND_OR_UNREADABLE'; fi"
            
            # Use send_command with strip_prompt and strip_command for cleaner output.
            output = self._connection.send_command(
                file_check_cmd, 
                strip_prompt=True, 
                strip_command=True
            )

            if "NOT_FOUND_OR_UNREADABLE" in output:
                raise FileNotFoundError(f"Remote file {remote_file_path} does not exist, is not a regular file, or is not readable. Server output: {output.strip()}")

            # 2. Determine local path
            if local_file_path is None:
                # Create 'temp_downloads' in the current working directory if it doesn't exist.
                project_root_temp_dir = "temp_downloads" 
                if not os.path.exists(project_root_temp_dir):
                    os.makedirs(project_root_temp_dir)
                local_file_name = os.path.basename(remote_file_path)
                local_file_path = os.path.join(project_root_temp_dir, local_file_name)
            
            # Ensure local_file_path is absolute and directory exists
            local_file_path = os.path.abspath(local_file_path)
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # 3. Attempt direct download (SFTP via Paramiko)
            try:
                if not hasattr(self._connection, 'remote_conn') or self._connection.remote_conn is None:
                    # This can happen if the connection object isn't the expected Paramiko-backed one.
                    raise AttributeError("SFTP not available: remote_conn (Paramiko transport) not found on Netmiko connection object.")

                sftp = self._connection.remote_conn.open_sftp()
                sftp.get(remote_file_path, local_file_path)
                sftp.close()
                print(f"File '{remote_file_path}' downloaded successfully to '{local_file_path}' (SFTP).")

            except Exception as e: # Broad exception for SFTP failure
                print(f"Direct SFTP download failed: {e}. Attempting with 'sudo cat'.")
                
                # 4. Attempt with sudo cat
                # This approach assumes passwordless sudo or sudo configured not to require a TTY.
                # It also assumes the file is text and not excessively large for send_command.
                sudo_download_cmd = f"sudo cat '{remote_file_path}'"
                
                try:
                    file_content = self._connection.send_command(
                        sudo_download_cmd,
                        strip_prompt=True, 
                        strip_command=True
                        # `expect_string` could be added here if a sudo password prompt is anticipated
                        # and needs to be handled by sending self.password or self.secret.
                        # However, robust interactive sudo is complex with send_command.
                    )
                    
                    # Basic checks for errors in sudo cat output
                    # A more robust check would involve checking stderr if possible, or specific error codes.
                    if "No such file or directory" in file_content or \
                       "cannot open" in file_content or \
                       "Permission denied" in file_content and "sudo" in file_content.lower() or \
                       "command not found" in file_content:
                         raise PermissionError(f"'sudo cat' download attempt failed for '{remote_file_path}'. Output: '{file_content.strip()}'")
                    
                    # If sudo prompts for a password and it's captured in file_content, it's a failure.
                    # This check is basic and might have false positives if the file contains this exact string.
                    if f"[sudo] password for {self.user}:" in file_content:
                        raise PermissionError(f"'sudo cat' download attempt for '{remote_file_path}' failed due to sudo password prompt. Ensure passwordless sudo or correct 'secret' configuration if sudo requires a password.")

                    # Write the captured content to the local file.
                    # Ensure to write as bytes if dealing with binary files, requires send_command_expect_binary or similar.
                    # For text files, encoding must be handled (assuming UTF-8).
                    with open(local_file_path, 'wb') as f: # Open in binary mode to write encoded bytes
                        f.write(file_content.encode('utf-8')) 

                    print(f"File '{remote_file_path}' downloaded successfully to '{local_file_path}' (using 'sudo cat').")

                except Exception as sudo_e: # Catch exceptions from send_command or file write
                    raise PermissionError(f"'sudo cat' download attempt for '{remote_file_path}' failed: {sudo_e}")

            return local_file_path

        finally:
            self.close_connection() # Ensure connection is closed regardless of success or failure

    def upload_file(self, local_file_path: str, remote_file_path: str) -> None:
        '''
        Uploads a local file to the remote host.

        Args:
            local_file_path: Absolute path of the local file to upload.
            remote_file_path: Absolute path on the remote host where the file should be uploaded.

        Raises:
            FileNotFoundError: If the local file does not exist.
            RemoteHostConnectionError: If connection fails.
            PermissionError: If remote operations (mkdir, mv, chown, chmod) fail.
            Exception: For other underlying errors during transfer or command execution.
        '''
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Local file {local_file_path} not found.")

        self.create_connection()
        sftp = None # Initialize sftp client variable
        try:
            if not hasattr(self._connection, 'remote_conn') or self._connection.remote_conn is None:
                raise AttributeError("SFTP not available: remote_conn (Paramiko transport) not found on Netmiko connection object.")
            
            sftp = self._connection.remote_conn.open_sftp()
            
            original_ownership_permissions = None
            remote_target_dir = os.path.dirname(remote_file_path)
            remote_target_filename = os.path.basename(remote_file_path)

            # 1. Ensure remote target directory exists
            try:
                sftp.stat(remote_target_dir)
            except FileNotFoundError:
                self._connection.send_command(f"mkdir -p {remote_target_dir}", strip_prompt=True, strip_command=True)
                try:
                    sftp.stat(remote_target_dir)
                    print(f"Created remote directory {remote_target_dir}")
                except FileNotFoundError:
                    raise PermissionError(f"Failed to create remote directory {remote_target_dir}. Check permissions or path.")

            # 2. Check if remote file exists for backup
            try:
                sftp.stat(remote_file_path)
                print(f"Remote file {remote_file_path} exists. Proceeding with backup.")
                
                stat_cmd = f"stat -c '%U:%G %a' {remote_file_path}"
                # Use strip_prompt=True, strip_command=True for cleaner output from stat
                stat_output = self._connection.send_command(stat_cmd, strip_prompt=True, strip_command=True).strip()
                if stat_output and ' ' in stat_output and len(stat_output.split(':')) == 2 and len(stat_output.split(' ')[0].split(':')) == 2 : # Basic sanity check
                    original_ownership_permissions = stat_output
                    print(f"Original ownership and permissions: {original_ownership_permissions}")
                else:
                    print(f"Warning: Could not retrieve original ownership/permissions for {remote_file_path}. Stat output: '{stat_output}'")

                backup_dir_name = "backup_files"
                backup_dir_path = os.path.join(remote_target_dir, backup_dir_name)
                self._connection.send_command(f"mkdir -p {backup_dir_path}", strip_prompt=True, strip_command=True)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                backup_filename = f"{remote_target_filename}_{timestamp}"
                backup_file_path = os.path.join(backup_dir_path, backup_filename)
                
                copy_cmd = f"cp {remote_file_path} {backup_file_path}"
                copy_output = self._connection.send_command(copy_cmd, strip_prompt=True, strip_command=True)
                # Check if copy_output indicates failure (it might be empty on success)
                # A more robust check would be `send_command_timing` and checking for errors, or `test -f {backup_file_path}` afterwards
                # For now, this relies on keywords.
                if "cannot open" in copy_output.lower() or "permission denied" in copy_output.lower() or "no such file" in copy_output.lower():
                    print(f"Direct cp failed for backup. Attempting with sudo. Output: {copy_output}")
                    sudo_copy_cmd = f"sudo cp {remote_file_path} {backup_file_path}"
                    sudo_copy_output = self._connection.send_command(sudo_copy_cmd, strip_prompt=True, strip_command=True) # Removed expect_string for now
                    if "cannot open" in sudo_copy_output.lower() or "permission denied" in sudo_copy_output.lower() or "no such file" in sudo_copy_output.lower():
                         raise PermissionError(f"Failed to backup {remote_file_path} to {backup_file_path} even with sudo. Error: {sudo_copy_output}")
                print(f"Backed up {remote_file_path} to {backup_file_path}")

                if original_ownership_permissions:
                    owner_group, perms = original_ownership_permissions.split(' ')
                    chown_backup_cmd = f"sudo chown {owner_group} {backup_file_path}"
                    chmod_backup_cmd = f"sudo chmod {perms} {backup_file_path}"
                    self._connection.send_command(chown_backup_cmd, strip_prompt=True, strip_command=True)
                    self._connection.send_command(chmod_backup_cmd, strip_prompt=True, strip_command=True)
                    print(f"Applied ownership {owner_group} and permissions {perms} to backup {backup_file_path}")

            except FileNotFoundError:
                print(f"Remote file {remote_file_path} does not exist. No backup needed.")
            except Exception as e:
                # Log this error but proceed with upload; backup failure shouldn't always block upload.
                print(f"Warning: An error occurred during backup check/process for {remote_file_path}: {e}")


            # 3. Upload to a temporary remote location
            remote_temp_upload_dir_base = "/tmp/nautodog_uploads"
            self._connection.send_command(f"mkdir -p {remote_temp_upload_dir_base}", strip_prompt=True, strip_command=True)
            
            upload_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            remote_temp_upload_dir = os.path.join(remote_temp_upload_dir_base, upload_timestamp)
            self._connection.send_command(f"mkdir -p {remote_temp_upload_dir}", strip_prompt=True, strip_command=True)

            temp_remote_file_path = os.path.join(remote_temp_upload_dir, remote_target_filename)
            
            sftp.put(local_file_path, temp_remote_file_path)
            print(f"Uploaded {local_file_path} to temporary remote path {temp_remote_file_path}")

            # 4. Move file from temporary location to final destination using sudo
            move_cmd = f"sudo mv {temp_remote_file_path} {remote_file_path}"
            move_output = self._connection.send_command(move_cmd, strip_prompt=True, strip_command=True)
            if "mv: cannot move" in move_output.lower() or "permission denied" in move_output.lower() or "no such file" in move_output.lower():
                # Check if the target file exists after mv, as sudo mv might not return verbose errors but still fail
                check_target_cmd = f"sudo test -f {remote_file_path} && echo EXISTS || echo NOT_EXISTS"
                target_status = self._connection.send_command(check_target_cmd, strip_prompt=True, strip_command=True)
                if "NOT_EXISTS" in target_status:
                    raise PermissionError(f"Failed to move file from {temp_remote_file_path} to {remote_file_path} using sudo. Error: {move_output}. Target check: {target_status}")
            print(f"Successfully moved {temp_remote_file_path} to {remote_file_path}")

            # 5. Apply original ownership and permissions if a backup was made
            if original_ownership_permissions:
                owner_group, perms = original_ownership_permissions.split(' ')
                chown_final_cmd = f"sudo chown {owner_group} {remote_file_path}"
                chmod_final_cmd = f"sudo chmod {perms} {remote_file_path}"
                self._connection.send_command(chown_final_cmd, strip_prompt=True, strip_command=True)
                self._connection.send_command(chmod_final_cmd, strip_prompt=True, strip_command=True)
                print(f"Applied original ownership {owner_group} and permissions {perms} to {remote_file_path}")
            else:
                print(f"No original ownership/permissions to apply (e.g., file is new). System defaults after 'sudo mv' will apply.")

            # 6. Clean up the remote temporary upload directory
            cleanup_cmd = f"rm -rf {remote_temp_upload_dir}"
            # This command is run as the connected user, not sudo.
            self._connection.send_command(cleanup_cmd, strip_prompt=True, strip_command=True)
            print(f"Cleaned up remote temporary directory {remote_temp_upload_dir}")

            print(f"File {local_file_path} uploaded successfully to {remote_file_path}.")
            if original_ownership_permissions: # To ensure backup_filename is defined
                print(f"Original file may have been backed up in {backup_dir_path}/ directory.")

        except AttributeError as ae: # Specifically catch if SFTP is not available
             raise RemoteHostConnectionError(f"SFTP client not available: {ae}") from ae
        except Exception as e:
            # More specific error handling can be added here for sftp specific errors if needed
            # For example, distinguishing between SFTP errors and send_command errors
            raise Exception(f"Upload failed: {e}")
        finally:
            if sftp:
                sftp.close()
            self.close_connection()

if __name__ == '__main__':
    # Basic example for testing - replace with actual details.
    # This section is for informal testing and will likely require a live SSH server.
    print("Attempting to test RemoteHost (requires a test SSH server and credentials correctly set up)")
    try:
        # Example: test_host = RemoteHost("your_server_ip", "your_user", password="your_password")
        # Or for key-based: test_host = RemoteHost("your_server_ip", "your_user", ssh_key_path="/path/to/your/key")
        
        # test_host = RemoteHost(host="localhost", user="your_user", password="your_password") # Replace with actuals
        
        # Create a dummy file on the remote for download testing (manual setup usually needed)
        # E.g., on remote: echo "Test content for download" > /tmp/remote_test_file.txt
        # remote_file = "/tmp/remote_test_file.txt"
        # local_dl_path = test_host.download_file(remote_file)
        # print(f"File downloaded to: {local_dl_path}")
        # with open(local_dl_path, 'r') as f:
        #     print(f"Content of downloaded file: {f.read()}")

        # Create a dummy local file for upload testing
        # with open("local_test_upload.txt", "w") as f:
        #     f.write("This is a test file for upload.")
        # test_host.upload_file("local_test_upload.txt", "/tmp/uploaded_local_file.txt")
        # print("Attempted upload.")
        
        print("RemoteHost class defined. Manual testing with a live SSH server is recommended.")
        print("Ensure 'temp_downloads' directory can be created or adjust 'project_root_temp_dir'.")

    except ValueError as ve:
        print(f"Configuration error: {ve}")
    except RemoteHostConnectionError as ce:
        print(f"Connection test failed: {ce}")
    except FileNotFoundError as fnfe:
        print(f"File operation failed: {fnfe}")
    except PermissionError as pe:
        print(f"Permission issue: {pe}")
    except ImportError:
        print("Netmiko library not found. Please install it: pip install netmiko")
    except Exception as e:
        print(f"An unexpected error occurred during __main__ test: {e}")
