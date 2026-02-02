
from automojo.testbase import verification
from automojo.testbase.mocking import Mock, create_instance_patch
from automojo.landscaping.layers.landscapeoperationallayer import LandscapeOperationalLayer

class DummyContextManager:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

def test_activate_coordinators_order() -> None:
    # Shared list to track call order
    call_order = []

    # Helper to record calls
    def record_call(name):
        def _side_effect(*args, **kwargs):
            call_order.append(name)
            return None # Default return
        return _side_effect

    # Helper for methods that need to return a list (like get_control_extensions)
    def record_call_return_list(name):
        def _side_effect(*args, **kwargs):
            # call_order.append(name) # We don't care about this one for the ordering check
            return []
        return _side_effect

    # Setup mocks
    mock_lscape = Mock()
    mock_integ_layer = Mock()

    mock_lscape.layer_integration = mock_integ_layer

    # Context Manager Mock using a helper class
    mock_context_manager = DummyContextManager()

    mock_lscape.begin_locked_landscape_scope = Mock(return_value=mock_context_manager)

    # Mock Coordinators
    mock_svc_coord = Mock()
    mock_svc_coord.creates_control_extensions = True
    mock_svc_coord.get_control_extensions = Mock(side_effect=record_call_return_list("svc_get_ext"))
    mock_svc_coord.activate = Mock(side_effect=record_call("svc_activate"))

    mock_pwr_coord = Mock()
    mock_pwr_coord.creates_control_extensions = True
    mock_pwr_coord.get_control_extensions = Mock(side_effect=record_call_return_list("pwr_get_ext"))
    mock_pwr_coord.activate = Mock(side_effect=record_call("pwr_activate"))

    mock_serial_coord = Mock()
    mock_serial_coord.creates_control_extensions = True
    mock_serial_coord.get_control_extensions = Mock(side_effect=record_call_return_list("serial_get_ext"))
    mock_serial_coord.activate = Mock(side_effect=record_call("serial_activate"))

    mock_dev_coord = Mock()
    mock_dev_coord.activate = Mock(side_effect=record_call("dev_activate"))

    mock_integ_layer.coordinators_for_services = {'svc': mock_svc_coord}
    mock_integ_layer.coordinators_for_power = {'pwr': mock_pwr_coord}
    mock_integ_layer.coordinators_for_serial = {'serial': mock_serial_coord}
    mock_integ_layer.coordinators_for_devices = {'dev': mock_dev_coord}

    # Mock Devices
    mock_device = Mock()
    mock_device.is_configured_for_power = True
    mock_device.is_configured_for_serial = True
    mock_device.attach_to_power = Mock(side_effect=record_call("attach_power"))
    mock_device.attach_to_serial = Mock(side_effect=record_call("attach_serial"))

    mock_integ_layer.integrated_devices = {'dev1': mock_device}

    # Initialize Layer
    layer = LandscapeOperationalLayer(mock_lscape)

    # Use create_instance_patch for establish_connectivity
    with create_instance_patch(layer, 'establish_connectivity') as mock_establish_conn:
        mock_establish_conn.configure(side_effect=record_call("establish_conn"))

        # Call the method
        activation_params = Mock()
        layer.activate_coordinators(activation_params)

        # Verify Order
        print(f"Call Order: {call_order}")

        try:
            conn_idx = call_order.index('establish_conn')
            power_idx = call_order.index('attach_power')
            dev_idx = call_order.index('dev_activate')

            verification.assert_greater(conn_idx, power_idx, "establish_connectivity should be called AFTER attach_to_power")
            verification.assert_greater(conn_idx, dev_idx, "establish_connectivity should be called AFTER dev_activate")
        except ValueError as e:
            verification.assert_fail(f"Expected call missing from order list: {e}. Order was: {call_order}")
