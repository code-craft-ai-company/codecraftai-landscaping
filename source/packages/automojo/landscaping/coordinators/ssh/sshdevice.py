"""
    .. module:: sshdevice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`SshDevice` class.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from automojo.errors.exceptions import SemanticError

from automojo.landscaping.landscapedevice import LandscapeDevice
from automojo.landscaping.friendlyidentifier import FriendlyIdentifier

from automojo.interop.protocols.ssh.sshagent import SshAgent

if TYPE_CHECKING:
    from automojo.landscaping.landscape import Landscape
    from automojo.landscaping.coordinatorbase import CoordinatorBase

# Canonical extension key for the SSH protocol extension.  Centralised here so
# the producer side (SshCoordinator.create_ssh_agent → device.attach_extension)
# and the consumer side (this property) cannot drift apart.
_SSH_EXTENSION_KEY = "network/ssh"


class SshDevice(LandscapeDevice):
    """
        Represents a device that can be accessed via SSH.
    """

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, device_type: str, device_config: dict):
        """
            Constructs an :class:`SshDevice` instance.

            :param lscape: Owning landscape instance.
            :param coordinator: Coordinator responsible for this device.
            :param friendly_id: Friendly identifier for the device.
            :param device_type: The declared device type.
            :param device_config: Configuration dictionary.
        """
        super().__init__(lscape, coordinator, friendly_id, device_type, device_config)

        self._host = device_config["host"]
        return

    @property
    def host(self) -> str:
        """
            Host name or address of the device.
        """
        return self._host

    @property
    def ssh(self) -> SshAgent:
        """
            Returns the :class:`SshAgent` extension associated with this device.

            :raises SemanticError: When no SSH extension has been attached to this
                                   device.  This indicates API misuse — either the
                                   coordinator failed to attach the extension during
                                   landscape activation, or a caller is using a device
                                   that was never wired for SSH.
        """
        if _SSH_EXTENSION_KEY not in self._extensions:
            err_msg_lines = [
                "No SSH protocol extension is attached to this device.",
                "    DEVICE: {}".format(self._friendly_id.full_identifier),
                "    EXPECTED EXTENSION KEY: {}".format(_SSH_EXTENSION_KEY),
                "    ATTACHED EXTENSION KEYS: {}".format(sorted(self._extensions.keys())),
            ]
            err_msg = "\n".join(err_msg_lines)
            raise SemanticError(err_msg)
        ext = self._extensions[_SSH_EXTENSION_KEY]
        return ext

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return
