
import posixpath
import shlex

from ccai.errors.exceptions import CommandError, SemanticError
from ccai.testbase import mocking
from ccai.testbase import verification
from ccai.testbase.mocking import Mock

import ccai.landscaping.clients.linux.ext.commandsext as commandsext_module
from ccai.landscaping.clients.linux.ext.commandsext import CommandsExt
from ccai.landscaping.clients.linux.ext.configureext import ConfigureExt
from ccai.landscaping.clients.linux.linuxclientcoordinator import LinuxClientCoordinator


class LocalMagicMock(Mock):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('recursive', True)
        super().__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


def test_bug_cifs_mount_arguments():
    """
    Regression test for cifs_mount calling session.run_cmd() without arguments.
    """
    mock_client = LocalMagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = LocalMagicMock()
    mock_session.run_cmd.return_value = (0, "stdout", "stderr")
    mock_session.directory_exists.return_value = True

    mock_sysctx = LocalMagicMock()
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
    Regression test ensuring cifs_mount includes the constructed options in the mount command.  The option
    values are not wrapped in double quotes: the whole argument is already shell-quoted and mount.cifs does
    not strip quotes, so quote characters would become part of the credentials.
    """
    mock_client = LocalMagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = LocalMagicMock()
    mock_session.run_cmd.return_value = (0, "stdout", "stderr")
    mock_session.directory_exists.return_value = True

    mock_sysctx = LocalMagicMock()
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

    # Check for options: one comma separated -o argument with unquoted values
    argv = shlex.split(cmd)
    expected_argv = [
        "mount", "-t", "cifs", "-o", "username=myuser,password=mypass,domain=mydomain",
        "//server/share", "/mnt/point"
    ]
    verification.assert_equal(argv, expected_argv)
    verification.assert_equal('"' in cmd, False)

def test_bug_unpacking_order():
    """
    Regression test for variable unpacking order in CommandsExt methods.
    It was unpacking as status, stderr, stdout. Should be status, stdout, stderr.
    """
    mock_client = LocalMagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = LocalMagicMock()
    # Return distinct strings to identify which is which
    # standard return is (status, stdout, stderr)
    mock_session.run_cmd.return_value = (1, "MY_STDOUT", "MY_STDERR")
    mock_session.directory_exists.return_value = True

    mock_sysctx = LocalMagicMock()
    mock_sysctx.open_session.return_value = mock_session
    mock_client.get_default_system_context.return_value = mock_sysctx

    cmd_ext = CommandsExt(mock_client)

    # Patch format_command_result to verify what arguments are passed to it.
    # The code passes stdout and stderr to format_command_result when status != 0.

    with mocking.create_module_patch(commandsext_module, "format_command_result") as mock_fmt:
        mock_fmt.return_value = "Formatted Error"

        # We need to suppress the exception or catch it
        try:
            cmd_ext.cifs_mount("//server/share", "/mnt/point", "user", "pass")
        except CommandError:
            # Expected: the mocked non-zero status makes cifs_mount raise; only the arguments
            # passed to format_command_result are verified below.
            pass

        # check call to format_command_result
        # The signature in code: format_command_result(errmsg, mount_cmd, status, stdout, stderr, exp_status=0)

        verification.assert_equal(mock_fmt.call_count > 0, True)

        args, _ = mock_fmt.call_args
        # args[3] is stdout, args[4] is stderr

        verification.assert_equal(args[3], "MY_STDOUT")
        verification.assert_equal(args[4], "MY_STDERR")

def test_bug_sudo_method_name():
    """
    Regression test for the method name typo in ConfigureExt.
    Should be enable_no_password_sudo.
    """
    mock_client = LocalMagicMock()
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
    mock_client = LocalMagicMock()
    mock_client.ipaddr = "1.2.3.4"

    mock_session = LocalMagicMock()
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


def _create_cifs_command_ext(run_cmd_results):
    """
        Creates a :class:`CommandsExt` over a mocked client whose session returns the given run_cmd results.

        :returns: A tuple of the extension, the mocked session and the mocked client (keep the client alive,
                  the extension only holds a weak reference to it).
    """
    mock_client = LocalMagicMock()
    mock_client.ipaddr = "1.2.3.4"

    scripted_results = list(run_cmd_results)

    def scripted_run_cmd(*args, **kwargs):
        result = scripted_results.pop(0)
        return result

    mock_session = LocalMagicMock()
    mock_session.run_cmd.side_effect = scripted_run_cmd
    mock_session.directory_exists.return_value = True

    mock_sysctx = LocalMagicMock()
    mock_sysctx.open_session.return_value = mock_session
    mock_client.get_default_system_context.return_value = mock_sysctx

    cmd_ext = CommandsExt(mock_client)
    return cmd_ext, mock_session, mock_client


def _run_commands(mock_session):
    """
        Returns the commands passed to the mocked session's run_cmd.
    """
    commands = []
    for args, _ in mock_session.run_cmd.call_args_list:
        commands.append(args[0])
    return commands


def test_cifs_mount_passes_credential_characters_literally():
    """
        Spaces, quotes, backslashes and shell metacharacters in the credentials reach mount.cifs unchanged
        inside the single mount option argument.
    """
    cmd_ext, mock_session, mock_client = _create_cifs_command_ext([(0, "", ""), (0, "", "")])

    cmd_ext.cifs_mount("//server/share", "/mnt/point", "my user", 'pa"ss\\$(id)=x\'y')

    argv = shlex.split(_run_commands(mock_session)[1])
    verification.assert_equal(argv[:4], ["mount", "-t", "cifs", "-o"])
    verification.assert_equal(argv[4], 'username=my user,password=pa"ss\\$(id)=x\'y')
    verification.assert_equal(argv[5:], ["//server/share", "/mnt/point"])


def test_cifs_mount_passes_a_password_with_a_comma_in_the_environment():
    """
        mount.cifs cannot parse a password containing a comma from its options and reads it from the PASSWD
        environment variable instead, so such a password is passed with ``env PASSWD=...`` and left out of
        the ``-o`` option.
    """
    cmd_ext, mock_session, mock_client = _create_cifs_command_ext([(0, "", ""), (0, "", "")])

    cmd_ext.cifs_mount("//server/share", "/mnt/point", "myuser", "pa,ss", domain="mydomain")

    argv = shlex.split(_run_commands(mock_session)[1])
    expected_argv = [
        "env", "PASSWD=pa,ss", "mount", "-t", "cifs", "-o", "username=myuser,domain=mydomain",
        "//server/share", "/mnt/point"
    ]
    verification.assert_equal(argv, expected_argv)


def test_cifs_mount_rejects_a_comma_in_the_username_or_domain():
    """
        A comma in the user name or the domain cannot be passed to mount.cifs, so it raises a SemanticError
        naming the option before any command runs on the client.
    """
    for username, domain, option_name in [("my,user", None, "username"), ("myuser", "my,domain", "domain")]:
        cmd_ext, mock_session, mock_client = _create_cifs_command_ext([])

        raised = None
        try:
            cmd_ext.cifs_mount("//server/share", "/mnt/point", username, "pass", domain=domain)
        except SemanticError as xcpt:
            raised = xcpt

        verification.assert_equal(raised is not None, True)
        verification.assert_equal(f"'{option_name}' cannot contain a comma" in str(raised), True)
        verification.assert_equal(mock_session.run_cmd.call_count, 0)


def test_cifs_mount_failure_redacts_the_password():
    """
        The command reported for a failing CIFS mount shows the password redacted, whether it was passed in
        the ``-o`` option or in PASSWD.
    """
    cases = [
        ("s3cret-value", "username=myuser,password=***"),
        ("s3cret,value", "env 'PASSWD=***' mount -t cifs -o username=myuser"),
    ]
    for password, expected_text in cases:
        cmd_ext, mock_session, mock_client = _create_cifs_command_ext([(0, "", ""), (1, "MY_STDOUT", "MY_STDERR")])

        raised = None
        try:
            cmd_ext.cifs_mount("//server/share", "/mnt/point", "myuser", password)
        except CommandError as xcpt:
            raised = xcpt

        verification.assert_equal(raised is not None, True)
        message = str(raised)
        verification.assert_equal(expected_text in message, True)
        verification.assert_equal("s3cret" in message, False)
