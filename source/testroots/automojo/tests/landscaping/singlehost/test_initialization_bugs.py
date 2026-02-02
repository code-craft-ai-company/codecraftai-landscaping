
from unittest.mock import MagicMock, patch
from automojo.testbase import verification
from automojo.landscaping.landscapeservice import LandscapeService
from automojo.landscaping.landscape import Landscape
from automojo.landscaping.coordinators.serial.tcp.tcpserialcoordinator import TcpSerialCoordinator
from automojo.landscaping.landscapedevice import LandscapeDevice

def test_landscape_service_repr_does_not_resolve_dns():
    lscape = MagicMock(spec=Landscape)
    lscape.credential_manager = MagicMock()
    coord = MagicMock()
    fid = MagicMock()
    fid.identity = "myservice"

    # Mock resolve during init
    with patch("socket.gethostbyname") as mock_resolve_init:
        mock_resolve_init.return_value = "1.2.3.4"
        # Service without IP config
        service = LandscapeService(lscape, coord, fid, "myservice", {"host": "myhost"})

    # Reset configured ip to None to simulate missing IP
    service._configured_ipaddr = None

    with patch("socket.gethostbyname") as mock_resolve:
        mock_resolve.return_value = "1.2.3.4"
        r = repr(service)

        verification.assert_equal(mock_resolve.call_count, 0, "repr() triggered DNS resolution.")

def test_tcp_serial_coordinator_uses_int_port_in_key():
    lscape = MagicMock(spec=Landscape)

    # Setup Coordinator
    coord = TcpSerialCoordinator(lscape)

    # Setup Device
    # Config with STRING port
    dev_config = {"host": "serialhost", "port": "2001"}

    # Create a mock device simulating TcpSerialDevice
    device = MagicMock()
    device.device_config = dev_config
    device.serial = MagicMock()

    # Inject into children
    with coord.begin_locked_coordinator_scope() as locked:
        coord._cl_children = {"serialhost": device}

    # Get extensions
    exts = coord.get_control_extensions()

    verification.assert_greater(len(exts), 0, "No extensions returned")

    key, _ = exts[0]

    # Expected behavior: uses int 2001 -> port=2001 (repr(2001) is '2001')
    verification.assert_true("port=2001" in key, f"Key does not contain int port representation: {key}")

def test_landscape_device_attach_to_serial_filters_extra_keys():
    lscape = MagicMock(spec=Landscape)
    lscape.credential_manager = MagicMock()
    coord = MagicMock()
    fid = MagicMock()
    fid.identity = "mydevice"

    # Device configured for serial with extra params
    dev_config = {
        "features": {
            "serial": {
                "host": "serialhost",
                "port": 2001,
                "baudrate": 9600
            }
        }
    }

    # Avoid resolving IP in init
    with patch("socket.gethostbyname"):
        device = LandscapeDevice(lscape, coord, fid, "mydevice", dev_config)

    # Mock checkout_control_point to verify what keys it receives
    lscape.checkout_control_point = MagicMock()
    lscape.checkout_control_point.return_value = MagicMock() # Mock extension

    device.attach_to_serial()

    kwargs = lscape.checkout_control_point.call_args[1]

    verification.assert_false("baudrate" in kwargs, "attach_to_serial passed extra 'baudrate' parameter.")
    verification.assert_true("host" in kwargs, "host not passed")
    verification.assert_true("port" in kwargs, "port not passed")
    verification.assert_equal(kwargs["port"], 2001, "port should be int 2001")
