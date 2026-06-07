
import shlex

from ccai.testbase import mocking
from ccai.testbase import verification
from ccai.testbase.mocking import Mock

from ccai.credentials.basiccredential import BasicCredential
from ccai.landscaping.clients.linux.linuxclient import LinuxClient

class LocalMagicMock(Mock):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('recursive', True)
        super().__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

def test_linux_client_uses_basic_credential():
    """
    Verifies that LinuxClient.open_sudo_ssh_session accepts a BasicCredential
    and uses the password from it.
    """

    # Arrange
    # Mock the landscape and coordinator as they are required by __init__
    mock_landscape = LocalMagicMock()
    mock_coordinator = LocalMagicMock()
    mock_friendly_id = LocalMagicMock()
    device_config = {"host": "1.2.3.4"}

    # Instantiate LinuxClient
    # LinuxClient.__init__ calls EXT_COMMANDS and EXT_CONFIGURE which take 'self'.
    # We create the client with mocks.
    client = LinuxClient(mock_landscape, mock_coordinator, mock_friendly_id, "linux", device_config)

    # Mock the ssh extension
    mock_ssh_agent = LocalMagicMock()
    # Manually inject the ssh extension since we didn't go through full landscape configuration
    client._extensions["network/ssh"] = mock_ssh_agent

    mock_session = LocalMagicMock()
    mock_session.run_cmd.return_value = (0, "stdout", "stderr")
    mock_ssh_agent.open_session.return_value = mock_session

    # Create a BasicCredential
    cred = BasicCredential(identifier="test", categories=["basic"], username="myuser", password="mypassword")

    # Act
    # This should call session.run_cmd with sudo -S and pass password via stdin
    client.open_sudo_ssh_session(cred)

    # Assert
    # Check that run_cmd was called
    verification.assert_equal(mock_session.run_cmd.call_count > 0, True)

    # Check that the password was used in the command
    # The code does: cmd = f"printf '%s\\n' {quoted_password} | sudo -S -v"

    quoted_password = shlex.quote("mypassword")
    expected_cmd_part = f"printf '%s\\n' {quoted_password}"

    found = False
    for call_args in mock_session.run_cmd.call_args_list:
        cmd = call_args[0][0]
        if expected_cmd_part in cmd:
            found = True
            break

    verification.assert_equal(found, True)
