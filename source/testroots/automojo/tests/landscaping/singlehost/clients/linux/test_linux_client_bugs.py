
import unittest.mock
from unittest.mock import MagicMock

from automojo.landscaping.clients.linux.ext.commandsext import CommandsExt
from automojo.landscaping.clients.linux.ext.configureext import ConfigureExt
from automojo.landscaping.clients.linux.linuxclientcoordinator import LinuxClientCoordinator

def test_bug_cifs_mount_arguments():
    """
    Regression test for cifs_mount calling session.run_cmd() without arguments.
    """
    mock_client = MagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.run_cmd.return_value = (0, "stdout", "stderr")
    mock_session.directory_exists.return_value = True

    mock_sysctx = MagicMock()
    mock_sysctx.open_session.return_value = mock_session
    mock_client.get_default_system_context.return_value = mock_sysctx

    cmd_ext = CommandsExt(mock_client)

    # Act
    cmd_ext.cifs_mount("//server/share", "/mnt/point", "user", "pass")

    # Assert
    # Verify that run_cmd was called with arguments (at least one call, checking the first one which was the bug)
    calls = mock_session.run_cmd.call_args_list
    assert len(calls) >= 2, "Expected at least 2 calls to run_cmd"

    # The first call was the mkdir command which was missing arguments
    mkdir_call = calls[0]
    args, _ = mkdir_call
    assert len(args) > 0, "session.run_cmd() called without arguments (mkdir)"
    assert "mkdir -p" in args[0], f"Expected mkdir command, got {args[0]}"

def test_bug_cifs_mount_options_inclusion():
    """
    Regression test ensuring cifs_mount includes the constructed options in the mount command.
    """
    mock_client = MagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.run_cmd.return_value = (0, "stdout", "stderr")
    mock_session.directory_exists.return_value = True

    mock_sysctx = MagicMock()
    mock_sysctx.open_session.return_value = mock_session
    mock_client.get_default_system_context.return_value = mock_sysctx

    cmd_ext = CommandsExt(mock_client)

    # Act
    cmd_ext.cifs_mount("//server/share", "/mnt/point", "myuser", "mypass", domain="mydomain")

    # Assert
    calls = mock_session.run_cmd.call_args_list
    assert len(calls) >= 2

    # The second call should be the mount command
    mount_call = calls[1]
    args, _ = mount_call
    cmd = args[0]

    # Check for options
    assert 'username="myuser"' in cmd, f"Command missing username option: {cmd}"
    assert 'password="mypass"' in cmd, f"Command missing password option: {cmd}"
    assert 'domain=mydomain' in cmd, f"Command missing domain option: {cmd}"
    assert '-o ' in cmd, f"Command missing -o flag: {cmd}"
    assert 'mount -t cifs' in cmd, f"Command missing mount prefix: {cmd}"

def test_bug_unpacking_order():
    """
    Regression test for variable unpacking order in CommandsExt methods.
    It was unpacking as status, stderr, stdout. Should be status, stdout, stderr.
    """
    mock_client = MagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    # Return distinct strings to identify which is which
    # standard return is (status, stdout, stderr)
    mock_session.run_cmd.return_value = (1, "MY_STDOUT", "MY_STDERR")
    mock_session.directory_exists.return_value = True

    mock_sysctx = MagicMock()
    mock_sysctx.open_session.return_value = mock_session
    mock_client.get_default_system_context.return_value = mock_sysctx

    cmd_ext = CommandsExt(mock_client)

    # Patch format_command_result to verify what arguments are passed to it.
    # The code passes stdout and stderr to format_command_result when status != 0.

    with unittest.mock.patch("automojo.landscaping.clients.linux.ext.commandsext.format_command_result") as mock_fmt:
        mock_fmt.return_value = "Formatted Error"

        # We need to suppress the exception or catch it
        try:
            cmd_ext.cifs_mount("//server/share", "/mnt/point", "user", "pass")
        except:
            pass

        # check call to format_command_result
        # The signature in code: format_command_result(errmsg, mount_cmd, status, stdout, stderr, exp_status=0)

        assert mock_fmt.called, "format_command_result was not called"

        args, _ = mock_fmt.call_args
        # args[3] is stdout, args[4] is stderr

        assert args[3] == "MY_STDOUT", f"Expected stdout='MY_STDOUT', got '{args[3]}'. Unpacking might be wrong."
        assert args[4] == "MY_STDERR", f"Expected stderr='MY_STDERR', got '{args[4]}'. Unpacking might be wrong."

def test_bug_sudo_method_name():
    """
    Regression test for the method name typo in ConfigureExt.
    Should be enable_no_password_sudo.
    """
    mock_client = MagicMock()
    config_ext = ConfigureExt(mock_client)

    assert hasattr(config_ext, "enable_no_password_sudo"), "ConfigureExt missing 'enable_no_password_sudo'"
    assert not hasattr(config_ext, "enabled_no_password_sudo"), "ConfigureExt still has typo 'enabled_no_password_sudo'"

def test_bug_coordinator_ssh_requirement():
    """
    Regression test for LinuxClientCoordinator.MUST_INCLUDE_SSH = True
    """
    assert getattr(LinuxClientCoordinator, "MUST_INCLUDE_SSH", False) is True, "LinuxClientCoordinator.MUST_INCLUDE_SSH should be True"
