
import posixpath
import shlex

from automojo.testbase import mocking
from automojo.testbase import verification
from automojo.testbase.mocking import MagicMock

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
    verification.assert_equal(len(calls) >= 2, True)

    # The first call was the mkdir command which was missing arguments
    mkdir_call = calls[0]
    args, _ = mkdir_call
    verification.assert_equal(len(args) > 0, True)
    verification.assert_equal("mkdir -p" in args[0], True)

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
    verification.assert_equal(len(calls) >= 2, True)

    # The second call should be the mount command
    mount_call = calls[1]
    args, _ = mount_call
    cmd = args[0]

    # Check for options
    verification.assert_equal('username="myuser"' in cmd, True)
    verification.assert_equal('password="mypass"' in cmd, True)
    verification.assert_equal('domain=mydomain' in cmd, True)
    verification.assert_equal('-o ' in cmd, True)
    verification.assert_equal('mount -t cifs' in cmd, True)

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

    with mocking.patch("automojo.landscaping.clients.linux.ext.commandsext.format_command_result") as mock_fmt:
        mock_fmt.return_value = "Formatted Error"

        # We need to suppress the exception or catch it
        try:
            cmd_ext.cifs_mount("//server/share", "/mnt/point", "user", "pass")
        except:
            pass

        # check call to format_command_result
        # The signature in code: format_command_result(errmsg, mount_cmd, status, stdout, stderr, exp_status=0)

        verification.assert_equal(mock_fmt.called, True)

        args, _ = mock_fmt.call_args
        # args[3] is stdout, args[4] is stderr

        verification.assert_equal(args[3], "MY_STDOUT")
        verification.assert_equal(args[4], "MY_STDERR")

def test_bug_sudo_method_name():
    """
    Regression test for the method name typo in ConfigureExt.
    Should be enable_no_password_sudo.
    """
    mock_client = MagicMock()
    config_ext = ConfigureExt(mock_client)

    verification.assert_equal(hasattr(config_ext, "enable_no_password_sudo"), True)
    verification.assert_equal(hasattr(config_ext, "enabled_no_password_sudo"), False)

def test_bug_coordinator_ssh_requirement():
    """
    Regression test for LinuxClientCoordinator.MUST_INCLUDE_SSH = True
    """
    verification.assert_equal(getattr(LinuxClientCoordinator, "MUST_INCLUDE_SSH", False), True)


def test_install_systemd_service_runtime_config_file_push():
    """
    Test that install_systemd_service pushes runtime_config_file to a temp location
    and then moves it to the destination using sudo.
    """
    mock_client = MagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None
    mock_session.run_cmd.return_value = (0, "stdout", "stderr")
    mock_session.is_service_running.return_value = False

    mock_client.ssh.open_session.return_value = mock_session

    config_ext = ConfigureExt(mock_client)

    svcname = "myservice"
    svcuser = "myuser"
    source_svc_config = "local/service.service"
    optfolder = "/opt/myservice"
    runtime_config = "local/config.json"

    # Act
    config_ext.install_systemd_service(svcname, svcuser, source_svc_config, optfolder=optfolder, runtime_config_file=runtime_config)

    # Assert
    # Check that file_push was called with a tmp path as destination
    # We expect session.file_push(runtime_config, tmp_path)
    # tmp_path should start with /tmp and end with config.json
    push_calls = mock_session.file_push.call_args_list

    # There are two pushes: one for runtime_config, one for source_svc_config
    # We need to find the one for runtime_config
    runtime_push_found = False
    tmp_runtime_path = None

    for args, _ in push_calls:
        src, dst = args
        if src == runtime_config:
            runtime_push_found = True
            verification.assert_equal(dst.startswith("/tmp/"), True)
            verification.assert_equal(dst.endswith("config.json"), True)
            tmp_runtime_path = dst
            break

    verification.assert_equal(runtime_push_found, True)

    # Check that sudo mv was called to move it to optfolder
    dest_runtime_path = posixpath.join(optfolder, "config.json")
    # We used shlex.quote in the code.
    quoted_tmp = shlex.quote(tmp_runtime_path)
    quoted_dest = shlex.quote(dest_runtime_path)

    mv_found = False
    for call_args in mock_session.run_cmd.call_args_list:
        cmd = call_args[0][0]
        if f"mv -f {quoted_tmp} {quoted_dest}" in cmd:
                mv_found = True
                break

    verification.assert_equal(mv_found, True)

    # Check that sudo chown was called for the file
    quoted_user = shlex.quote(svcuser)
    chown_pattern = f"chown {quoted_user}: {quoted_dest}"

    chown_found = False
    for call_args in mock_session.run_cmd.call_args_list:
        cmd = call_args[0][0]
        if chown_pattern in cmd:
                chown_found = True
                break

    verification.assert_equal(chown_found, True)
