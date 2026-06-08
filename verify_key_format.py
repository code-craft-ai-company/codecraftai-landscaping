
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add packages to path
sys.path.insert(0, os.path.abspath("source/packages"))

from ccai.landscaping.layers.landscapeoperationallayer import LandscapeOperationalLayer
from ccai.landscaping.services.power.dlipower.dlipowercoordinator import DliPowerCoordinator
from ccai.errors.exceptions import CheckoutError

class TestControlKeyFormat(unittest.TestCase):
    def test_key_generation_operational_layer(self):
        lscape = MagicMock()
        lscape.interactive_mode = False
        layer = LandscapeOperationalLayer(lscape)

        # Mock pool
        mock_ext = MagicMock()
        # Pre-populate with EXPECTED key format
        expected_key = "power: outlet=5 server='pdu-1'"
        layer._operational_controlpoint_pool[expected_key] = mock_ext

        # Test checkout with kwargs
        mock_lock = MagicMock()
        lscape.begin_locked_landscape_scope.return_value.__enter__.return_value = mock_lock

        # Kwargs order shouldn't matter if logic sorts them
        ext = layer.checkout_control_point("power", server="pdu-1", outlet=5)
        self.assertEqual(ext, mock_ext)

        # Test with different kwargs order
        layer._operational_controlpoint_pool[expected_key] = mock_ext # put back
        ext = layer.checkout_control_point("power", outlet=5, server="pdu-1")
        self.assertEqual(ext, mock_ext)

    def test_key_generation_coordinator(self):
        lscape = MagicMock()
        coord = DliPowerCoordinator(lscape, {})

        # Mock child service
        mock_svc = MagicMock()
        mock_svc.host = "pdu-1"
        mock_svc.credentials = {} # No creds = no extensions, need to mock

        # Mock credentials
        cred = MagicMock()
        cred.categories = ["basic"]
        mock_svc.credentials = {"c": cred}

        coord._cl_children = {"pdu-1": MagicMock()} # Mock internal structure if needed?
        # children_as_extension property uses _cl_children.values().extended
        # Mock children_as_extension directly on the instance if possible, or mock the property

        # DliPowerCoordinator uses self.children_as_extension which comes from CoordinatorBase
        # We need to mock that property or the underlying structure.

        # Let's just mock the get_control_extensions method's dependencies
        # Actually easier to just check the logic in a new test or trust the file write.
        # But let's try to run the code.

        # Mocking children_as_extension
        # It's a property. We can't mock it on an instance easily without patching the class or using a mock object AS the coordinator.

        # Let's instantiate the coordinator and mock what it needs.
        mock_device_wrapper = MagicMock()
        mock_device_wrapper.extended = mock_svc

        # Mocking internal dict
        coord._cl_children["pdu-1"] = mock_device_wrapper

        # Run
        extensions = coord.get_control_extensions()

        # Verify keys
        found = False
        expected_key = "power: outlet=1 server='pdu-1'"
        for key, ext in extensions:
            if key == expected_key:
                found = True
                break
        self.assertTrue(found, f"Expected key '{expected_key}' not found in {extensions}")

if __name__ == "__main__":
    unittest.main()
