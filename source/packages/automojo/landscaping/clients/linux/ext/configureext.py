"""
    .. module:: configureext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the configureext functionality.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import List, Optional, TYPE_CHECKING

import os
import weakref

from automojo.errors.exceptions import CommandError

from automojo.credentials.sshcredential import SshCredential
from automojo.xmodules.xformatting import format_command_result

from automojo.landscaping.clients.clientsourcepackager import ClientSourcePackager
from automojo.interop.protocols.ssh.sshsession import SshSession


if TYPE_CHECKING:
    from automojo.landscaping.clients.linux.linuxclient import LinuxClient


TEMPLATE_FILE_SUDO_CONFIG = "/etc/sudoers.d/77-automation-{username}"

class ConfigureExt:
    """
        Extension that configures a Linux client for automation.
    """

    REQUIRED_SYSTEM_PACKAGES = [
        'build-essential',
        'python3-dev',
        'zip'
    ]

    def __init__(self, client: "LinuxClient"):
        """
            Creates a :class:`ConfigureExt` instance bound to a client.

            :param client: The :class:`LinuxClient` this extension operates on.
        """
        self._client_ref = weakref.ref(client)
        return

    @property
    def client(self) -> "LinuxClient":
        """
            Returns the owning :class:`LinuxClient` instance.
        """
        return self._client_ref()

    def deploy_source_package(self, source_root: str, package_name: str, remote_source_root: str, cache_dir: Optional[str] = None,
                              force_repackage: Optional[bool]=False, force_deploy: Optional[bool]=False, basis_session: Optional[SshSession] = None):
        """
            Packages and deploys a source archive to the remote client.

            :param source_root: Local path to the source root directory.
            :param package_name: Name of the package archive to create/deploy.
            :param remote_source_root: Remote directory where the source is deployed.
            :param cache_dir: Directory used to store cached packages.
            :param force_repackage: Recreate the package even if it exists.
            :param force_deploy: Force the deployment even if already installed.
            :param basis_session: Optional session to base operations on.
        """

        client = self.client

        if cache_dir is None:
            cache_dir = os.path.join(source_root, ".cache")
        
        packager = ClientSourcePackager(source_root, cache_dir)

        skip_if_exists = not force_repackage

        packager.create_zip_package(package_name, skip_if_exists=skip_if_exists)

        source_env = packager.get_environment()

        with client.ssh.open_session(basis_session=basis_session) as session:

            python_version = self.get_python_version(basis_session=session)
            python_path_list = [
                f"{remote_source_root}/source/packages",
                f"{remote_source_root}/source/testroots/testplus",
                f"{remote_source_root}/.venv/lib/{python_version}/site-packages"
            ]
            python_path = ":".join(python_path_list)
        
            install_env = source_env.copy()
            install_env["PYTHON_VERSION"] = python_version
            install_env["PYTHONPATH"] = python_path

            packager.deploy_zip_package_via_ssh(session, package_name, install_env, remote_source_root, force_update=force_deploy)

        return


    def enable_no_password_sudo(self, sudo_username: Optional[str] = None, sudo_password: Optional[str] = None,
                                 basis_session: Optional[SshSession] = None):
        """
            Enables passwordless sudo for a given user on the remote machine.

            :param sudo_username: User name that should be granted sudo access.
            :param sudo_password: Password for the sudo user.
            :param basis_session: Optional session to base operations on.
        """
        
        client = self.client

        if sudo_username is None:
            sshcred: SshCredential = client.get_credentials_by_category("ssh")[0]

            sudo_username = sshcred.username
            sudo_password = sshcred.password

        fill_dict = {"username": sudo_username}
        user_cfg_file = TEMPLATE_FILE_SUDO_CONFIG.format(**fill_dict)

        with client.ssh.open_session(basis_session=basis_session) as session:

            sudo_file_exists_cmd = f"echo '{sudo_password}' | sudo -S bash -c \"[[ -f '{user_cfg_file}' ]] && echo 0 || echo 1\""
            status, stdout, stderr = session.run_cmd(sudo_file_exists_cmd)
            if int(stdout.strip()) == 1:

                sudo_grp_cmd = f"echo '{sudo_password}' | sudo -S usermod -aG sudo '{sudo_username}'"
                status, stdout, stderr = session.run_cmd(sudo_grp_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to add `{sudo_username}` to the 'sudo' user group.",
                                                sudo_grp_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

                sudo_user_cfg_cmd =  f"echo '{sudo_password}' | sudo -S bash -c \"echo '{sudo_username} ALL=(ALL) NOPASSWD: ALL' | EDITOR='tee -a' visudo -f '{user_cfg_file}'\""
                status, stdout, stderr = session.run_cmd(sudo_user_cfg_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while installing sudo config for user `{sudo_username}`.",
                                                sudo_user_cfg_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)
        
        return
    

    def get_python_version(self, basis_session: Optional[SshSession] = None):
        """
            Queries the remote machine for its Python version string.

            :param basis_session: Optional session to base operations on.

            :returns: The ``major.minor`` version string.
        """

        client = self.client

        python_version = None

        with client.ssh.open_session(basis_session=basis_session) as session:

            getpyver_cmd = "python3 -c \"import platform; print('python{}.{}'.format(*platform.python_version_tuple()[:2]))\""
            status, stdout, stderr = session.run_cmd(getpyver_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to get the python version from the remote machine.",
                                            getpyver_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            python_version = stdout.strip()

        return python_version


    def install_required_system_packages(self, basis_session: Optional[SshSession] = None):
        """
            Installs packages required for the automation environment.

            :param basis_session: Optional session to base operations on.
        """

        self.system_packages_install(self.REQUIRED_SYSTEM_PACKAGES, basis_session=basis_session)

        return


    def install_systemd_service(self, svcname: str, svcuser: str, source_svc_config_file: str, pidfolder: Optional[str] =  None,
                                optfolder: Optional[str] =  None, runtime_config_file: Optional[str] = None, basis_session: Optional[SshSession] = None):
        """
            Installs and enables a systemd service on the remote machine.

            :param svcname: The service name to install.
            :param svcuser: The user that owns the service.
            :param source_svc_config_file: Path to the local service configuration file.
            :param pidfolder: Optional pid directory path.
            :param optfolder: Optional opt directory path.
            :param runtime_config_file: Optional runtime configuration file to deploy.
            :param basis_session: Optional session to base operations on.
        """

        client = self.client

        final_dest_svc_config_file = f"/etc/systemd/system/{svcname}.service"
        tmp_dest_svc_config_file = f"/tmp/{svcname}.service"

        with client.ssh.open_session(basis_session=basis_session) as session:

            if optfolder is not None:
                mkdir_cmd = f"sudo mkdir -p {optfolder}"
                status, stdout, stderr = session.run_cmd(mkdir_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to create the opt folder for `{svcname}`.",
                                                mkdir_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

                chown_cmd = f"sudo chown {svcuser}: {optfolder}"
                status, stdout, stderr = session.run_cmd(chown_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to change the ownership of the opt folder for `{svcname}`.",
                                                chown_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)
                
                if runtime_config_file is not None:

                    dest_base_name = os.path.basename(runtime_config_file)
                    dest_runtime_config_file = os.path.join(optfolder, dest_base_name)

                    session.file_push(runtime_config_file, dest_runtime_config_file)

            if pidfolder is not None:
                mkdir_cmd = f"sudo mkdir -p {pidfolder}"
                status, stdout, stderr = session.run_cmd(mkdir_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to create the pid folder for `{svcname}`.",
                                                mkdir_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

                chown_cmd = f"sudo chown {svcuser}: {pidfolder}"
                status, stdout, stderr = session.run_cmd(chown_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to change the ownership of pid folder for `{svcname}`.",
                                                chown_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

            stop_svc_cmd = f"sudo systemctl stop {svcname}"
            session.run_cmd(stop_svc_cmd)

            rm_svc_cfg_cmd = f"sudo rm -f {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(rm_svc_cfg_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to remove the config file for `{svcname}` service.",
                                            rm_svc_cfg_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            session.file_push(source_svc_config_file, tmp_dest_svc_config_file)

            enable_svc_cmd = f"sudo cp -f {tmp_dest_svc_config_file} {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(enable_svc_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to install `{svcname}` service config file.",
                                            enable_svc_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            chown_cmd = f"sudo chown root {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(chown_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to change `{svcname}` service config file owner.",
                                            chown_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            chmod_cmd = f"sudo chmod 644 {final_dest_svc_config_file}"
            status, stdout, stderr = session.run_cmd(chmod_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to change `{svcname}` service config permissions.",
                                            chmod_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            daemon_reload_cmd = f"sudo systemctl daemon-reload"
            status, stdout, stderr = session.run_cmd(daemon_reload_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to reload systemclt daemon.",
                                            daemon_reload_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            start_svc_cmd = f"sudo systemctl enable {svcname}"
            status, stdout, stderr = session.run_cmd(start_svc_cmd)
            if status != 0:
                errmsg = format_command_result(f"Error while attempting to start `{svcname}` service.",
                                            start_svc_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)

            if not self.is_service_running(svcname, basis_session=session):

                start_svc_cmd = f"sudo systemctl start {svcname}"
                status, stdout, stderr = session.run_cmd(start_svc_cmd)
                if status != 0:
                    errmsg = format_command_result(f"Error while attempting to start `{svcname}` service.",
                                                start_svc_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)

        return
    

    def is_service_running(self, svcname: str, basis_session: Optional[SshSession] = None):
        """
            Checks if a systemd service is running on the remote machine.

            :param svcname: Name of the service to query.
            :param basis_session: Optional session to base operations on.

            :returns: ``True`` if the service is running, otherwise ``False``.
        """

        client = self.client

        svc_running = False

        with client.ssh.open_session(basis_session=basis_session) as session:
            chk_svc_running_cmd = f"systemctl is-active --quiet {svcname} && echo $?"
            status, stdout, stderr = session.run_cmd(chk_svc_running_cmd)
            if status != 0:
                if stderr != "":
                    errmsg = format_command_result(f"Error while attempting to start `{svcname}` service.",
                                                chk_svc_running_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                    raise CommandError(errmsg, status, stdout, stderr)
                else:
                    svc_running = False
            else:
                svc_running = True

        return svc_running
    

    def system_packages_install(self, packages_to_install: List[str], basis_session: Optional[SshSession] = None):
        """
            Installs a list of system packages on the remote host.

            :param packages_to_install: List of package names to install.
            :param basis_session: Optional session to base operations on.
        """

        client = self.client

        with client.ssh.open_session(basis_session=basis_session) as session:

            for package in packages_to_install:
                ensure_cmd = f"apt list --installed | grep -E '^{package}/'"
                status, stdout, stderr = session.run_cmd(ensure_cmd)
                if status != 0:
                    # If the package is not found, install it.
                    install_cmd = f"sudo DEBIAN_FRONTEND=noninteractive apt -yq install {package}"
                    status, stdout, stderr = session.run_cmd(install_cmd)
                    if status != 0:
                        errmsg = format_command_result(f"Error while attempting to install the `{package}` system package.",
                                                    install_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                        raise CommandError(errmsg, status, stdout, stderr)

        return


    def system_packages_update(self, basis_session: Optional[SshSession] = None):
        """
            Updates the system package index on the remote client using apt.

            :param basis_session: Optional existing SSH session to reuse.
        """

        client = self.client

        with client.ssh.open_session(basis_session=basis_session) as session:

            apt_update_cmd = f"sudo apt update"
            status, stdout, stderr = session.run_cmd(apt_update_cmd)
            if status != 0:
                errmsg = format_command_result("Error attempting to the apt package list.",
                                            apt_update_cmd, status, stdout, stderr, exp_status=[0], target=client.ipaddr)
                raise CommandError(errmsg, status, stdout, stderr)
            
        return
