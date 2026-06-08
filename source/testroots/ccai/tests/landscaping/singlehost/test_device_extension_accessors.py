"""
    Tests for the device-side extension accessors.

    The ``SshDevice.ssh`` and ``TcpSerialDevice.serial`` properties read
    ``self._extensions[<key>]``.  Before the sixth-pass audit fix they would
    raise ``KeyError(<key>)`` if the extension had never been attached — a
    misleading low-level error.  After the fix they raise ``SemanticError``
    with a descriptive multi-line message naming the device, the expected
    extension key, and the actually-attached keys.
"""

from ccai.errors.exceptions import SemanticError

from ccai.testbase import verification

from ccai.landscaping.coordinators.ssh.sshdevice import SshDevice
from ccai.landscaping.coordinators.serial.tcp.tcpserialdevice import TcpSerialDevice
from ccai.landscaping.friendlyidentifier import FriendlyIdentifier


def _build_ssh_device(*, full_id: str = "host-1.example.com", hint: str = "host-1",
                      attached_extensions: dict = None) -> SshDevice:
    """
        Build a bare-bones :class:`SshDevice` without going through the full
        ``LandscapeDevice.__init__`` chain (which requires a Landscape).
    """
    if attached_extensions is None:
        attached_extensions = {}
    dev = object.__new__(SshDevice)
    dev._friendly_id = FriendlyIdentifier(full_identifier=full_id, hint=hint)
    dev._extensions = dict(attached_extensions)
    dev._host = full_id
    return dev


def _build_tcp_serial_device(*, full_id: str = "serial-1.example.com", hint: str = "serial-1",
                              attached_extensions: dict = None) -> TcpSerialDevice:
    """
        Build a bare-bones :class:`TcpSerialDevice` similarly.
    """
    if attached_extensions is None:
        attached_extensions = {}
    dev = object.__new__(TcpSerialDevice)
    dev._friendly_id = FriendlyIdentifier(full_identifier=full_id, hint=hint)
    dev._extensions = dict(attached_extensions)
    dev._host = full_id
    dev._port = 9000
    return dev


def test_sshdevice_ssh_property_raises_semantic_error_when_unattached() -> None:
    """
        Reading ``ssh`` on an :class:`SshDevice` whose ``_extensions`` map
        does not contain ``network/ssh`` raises :class:`SemanticError`.
    """
    dev = _build_ssh_device()
    raised = None
    try:
        _ = dev.ssh
    except SemanticError as exc:
        raised = exc
    verification.assert_true(raised is not None)
    return


def test_sshdevice_ssh_error_message_contains_device_id_and_key() -> None:
    """
        The SemanticError's message includes the device's full identifier
        and the expected extension key, so triage doesn't need to grep
        the source.
    """
    dev = _build_ssh_device(full_id="alpha.example.com", hint="alpha")
    try:
        _ = dev.ssh
    except SemanticError as exc:
        msg = str(exc)
        verification.assert_true("alpha.example.com" in msg)
        verification.assert_true("network/ssh" in msg)
    return


def test_sshdevice_ssh_returns_extension_when_attached() -> None:
    """
        When the SSH extension is attached, ``ssh`` returns it unchanged.
    """
    fake_ssh_ext = object()
    dev = _build_ssh_device(attached_extensions={"network/ssh": fake_ssh_ext})
    verification.assert_equal(dev.ssh, fake_ssh_ext)
    return


def test_sshdevice_ssh_lists_attached_keys_in_error() -> None:
    """
        When the device has OTHER extensions attached but not SSH, the
        error message lists what's actually attached so callers know
        what's available.
    """
    dev = _build_ssh_device(attached_extensions={"power": object(), "serial": object()})
    try:
        _ = dev.ssh
    except SemanticError as exc:
        msg = str(exc)
        verification.assert_true("power" in msg)
        verification.assert_true("serial" in msg)
    return


def test_tcpserialdevice_serial_property_raises_semantic_error_when_unattached() -> None:
    """
        Reading ``serial`` on a :class:`TcpSerialDevice` whose ``_extensions``
        map does not contain ``serial`` raises :class:`SemanticError`.
    """
    dev = _build_tcp_serial_device()
    raised = None
    try:
        _ = dev.serial
    except SemanticError as exc:
        raised = exc
    verification.assert_true(raised is not None)
    return


def test_tcpserialdevice_serial_error_message_contains_device_id_and_key() -> None:
    """
        The SemanticError's message includes the device's full identifier
        and the expected extension key.
    """
    dev = _build_tcp_serial_device(full_id="serial-host.example.com", hint="serial-host")
    try:
        _ = dev.serial
    except SemanticError as exc:
        msg = str(exc)
        verification.assert_true("serial-host.example.com" in msg)
        verification.assert_true("serial" in msg)
    return


def test_tcpserialdevice_serial_returns_extension_when_attached() -> None:
    """
        When the serial extension is attached, ``serial`` returns it.
    """
    fake_serial_ext = object()
    dev = _build_tcp_serial_device(attached_extensions={"serial": fake_serial_ext})
    verification.assert_equal(dev.serial, fake_serial_ext)
    return
