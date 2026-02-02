
import sys
import unittest
import importlib
from unittest.mock import MagicMock, call, Mock, patch

class TestStartupOrder(unittest.TestCase):

    def test_activate_coordinators_order(self):
        # Create a dictionary of mocks for sys.modules
        modules_to_mock = {
            'automojo.errors': MagicMock(),
            'automojo.errors.xtraceback': MagicMock(),
            'automojo.errors.exceptions': MagicMock(),
            'automojo.interfaces': MagicMock(),
            'automojo.interfaces.iexcludefilter': MagicMock(),
            'automojo.interfaces.iincludefilter': MagicMock(),
            'automojo.xmodules': MagicMock(),
            'automojo.xmodules.xlogging': MagicMock(),
            'automojo.xmodules.xlogging.enhancedloggers': MagicMock(),
            'automojo.testbase': MagicMock(),
            'automojo.testbase.coupling': MagicMock(),
            'automojo.testbase.coupling.integrationcoupling': MagicMock(),
            'automojo.landscaping.landscape': MagicMock(),
            'automojo.landscaping.landscapeparameters': MagicMock(),
            'automojo.landscaping.extensions.control.controlextension': MagicMock(),
            'automojo.landscaping.landscapedevice': MagicMock(),
            'automojo.landscaping.landscapedevicecluster': MagicMock(),
            'automojo.landscaping.landscapeservice': MagicMock(),
            'automojo.landscaping.clusters.nodecoordinatorbase': MagicMock(),
            'automojo.landscaping.constants': MagicMock(),
            'automojo.landscaping.coordinatorbase': MagicMock(),
            'automojo.landscaping.coupling': MagicMock(),
            'automojo.landscaping.coupling.coordinatorcoupling': MagicMock(),
            'automojo.landscaping.friendlyidentifier': MagicMock(),
            'automojo.landscaping.landscapedevicegroup': MagicMock(),
            'automojo.landscaping.layers.landscapeconfigurationlayer': MagicMock(),
        }

        with patch.dict(sys.modules, modules_to_mock):
            # We need to make sure we import/reload the module under test while the patch is active
            # This ensures it uses the mocked modules.

            # Since we are running in a potentially persistent environment, we should check if it's already imported
            import automojo.landscaping.layers.landscapeoperationallayer
            importlib.reload(automojo.landscaping.layers.landscapeoperationallayer)

            from automojo.landscaping.layers.landscapeoperationallayer import LandscapeOperationalLayer

            # Setup mocks
            mock_lscape = Mock()
            mock_integ_layer = Mock()
            mock_lscape.layer_integration = mock_integ_layer
            mock_lscape.begin_locked_landscape_scope.return_value.__enter__ = Mock()
            mock_lscape.begin_locked_landscape_scope.return_value.__exit__ = Mock()

            # Mock Coordinators
            mock_svc_coord = Mock()
            mock_svc_coord.creates_control_extensions = True
            mock_svc_coord.get_control_extensions.return_value = []

            mock_pwr_coord = Mock()
            mock_pwr_coord.creates_control_extensions = True
            mock_pwr_coord.get_control_extensions.return_value = []

            mock_serial_coord = Mock()
            mock_serial_coord.creates_control_extensions = True
            mock_serial_coord.get_control_extensions.return_value = []

            mock_dev_coord = Mock()

            mock_integ_layer.coordinators_for_services = {'svc': mock_svc_coord}
            mock_integ_layer.coordinators_for_power = {'pwr': mock_pwr_coord}
            mock_integ_layer.coordinators_for_serial = {'serial': mock_serial_coord}
            mock_integ_layer.coordinators_for_devices = {'dev': mock_dev_coord}

            # Mock Devices
            mock_device = Mock()
            mock_device.is_configured_for_power = True
            mock_device.is_configured_for_serial = True

            mock_integ_layer.integrated_devices = {'dev1': mock_device}

            # Initialize Layer
            layer = LandscapeOperationalLayer(mock_lscape)

            # Mock internal methods
            layer.establish_connectivity = Mock()

            # Manager for ordering
            manager = Mock()
            manager.attach_mock(mock_svc_coord.activate, 'svc_activate')
            manager.attach_mock(mock_pwr_coord.activate, 'pwr_activate')
            manager.attach_mock(mock_serial_coord.activate, 'serial_activate')
            manager.attach_mock(layer.establish_connectivity, 'establish_conn')
            manager.attach_mock(mock_device.attach_to_power, 'attach_power')
            manager.attach_mock(mock_device.attach_to_serial, 'attach_serial')
            manager.attach_mock(mock_dev_coord.activate, 'dev_activate')

            # Call the method
            activation_params = Mock()
            layer.activate_coordinators(activation_params)

            # Verify Order
            calls = [c[0] for c in manager.mock_calls]

            conn_idx = calls.index('establish_conn')
            power_idx = calls.index('attach_power')
            dev_idx = calls.index('dev_activate')

            self.assertGreater(conn_idx, power_idx, "establish_connectivity should be called AFTER attach_to_power")
            self.assertGreater(conn_idx, dev_idx, "establish_connectivity should be called AFTER dev_activate")

if __name__ == '__main__':
    unittest.main()
