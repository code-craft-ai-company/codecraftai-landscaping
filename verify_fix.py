import sys
import os
from unittest.mock import MagicMock

# 1. Setup path
sys.path.insert(0, os.path.abspath('source/packages'))

# Helper classes for mocks
class FeatureAttachedObject: pass
class BaseCredential: pass
class ProtocolExtension: pass
class LockedScope:
    def __init__(self, lock): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
class UnLockedScope:
    def __init__(self, lock): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass

def mock_package(name):
    m = MagicMock()
    m.__path__ = []
    sys.modules[name] = m
    return m

# 2. Mock external/missing dependencies

# Mock automojo.interfaces
mock_package('automojo.interfaces')
sys.modules['automojo.interfaces.iexcludefilter'] = MagicMock()
sys.modules['automojo.interfaces.iincludefilter'] = MagicMock()

# Mock automojo.testbase
mock_package('automojo.testbase')
mock_package('automojo.testbase.coupling')
sys.modules['automojo.testbase.coupling.integrationcoupling'] = MagicMock()

mock_features = MagicMock()
mock_features.FeatureAttachedObject = FeatureAttachedObject
sys.modules['automojo.testbase.features'] = mock_features

# Mock automojo.xmodules
mock_package('automojo.xmodules')
mock_package('automojo.xmodules.xlogging')

mock_enhancedloggers = MagicMock()
mock_enhancedloggers.getEnhancedLogger = MagicMock(return_value=MagicMock())
sys.modules['automojo.xmodules.xlogging.enhancedloggers'] = mock_enhancedloggers

mock_package('automojo.xmodules.xthreading')

mock_lockscopes = MagicMock()
mock_lockscopes.LockedScope = LockedScope
mock_lockscopes.UnLockedScope = UnLockedScope
sys.modules['automojo.xmodules.xthreading.lockscopes'] = mock_lockscopes

mock_package('automojo.xmodules.xcollections')
sys.modules['automojo.xmodules.xcollections.mergemap'] = MagicMock()

# Mock automojo.credentials
mock_package('automojo.credentials')

mock_basecred = MagicMock()
mock_basecred.BaseCredential = BaseCredential
sys.modules['automojo.credentials.basecredential'] = mock_basecred

sys.modules['automojo.credentials.sshcredential'] = MagicMock()
sys.modules['automojo.credentials.credentialmanager'] = MagicMock()
sys.modules['automojo.credentials.wellknown'] = MagicMock()

# Mock automojo.configuration
mock_package('automojo.configuration')
sys.modules['automojo.configuration.configurationmaps'] = MagicMock()

# Mock automojo.thisapp
mock_package('automojo.thisapp')
sys.modules['automojo.thisapp.contextpaths'] = MagicMock()
sys.modules['automojo.thisapp.wellknown'] = MagicMock()

# Mock automojo.interop
mock_package('automojo.interop')
mock_package('automojo.interop.interfaces')
sys.modules['automojo.interop.interfaces.isystemcontext'] = MagicMock()

mock_package('automojo.interop.protocols')
mock_package('automojo.interop.protocols.serial')
sys.modules['automojo.interop.protocols.serial.tcpserialagent'] = MagicMock()

# Mock automojo.errors
mock_package('automojo.errors')
sys.modules['automojo.errors.exceptions'] = MagicMock()

# Mock protocol extension
mock_pe_module = MagicMock()
mock_pe_module.ProtocolExtension = ProtocolExtension
mock_package('automojo.landscaping.protocolextensions')
sys.modules['automojo.landscaping.protocolextensions.protocolextension'] = mock_pe_module


sys.modules['yaml'] = MagicMock()

# 3. Import packages

import automojo.landscaping
import automojo.landscaping.services
import automojo.landscaping.services.power
import automojo.landscaping.services.power.dlipower
import automojo.landscaping.coordinators
import automojo.landscaping.coordinators.serial
import automojo.landscaping.coordinators.serial.tcp


import unittest
from automojo.landscaping.layers.landscapeintegrationlayer import LandscapeIntegrationLayer
from automojo.landscaping.services.power.dlipower.dlipowercoordinatorcoupling import DLIPowerServiceCoordinatorCoupling
from automojo.landscaping.coordinators.serial.tcp.tcpserialcoordinatorcoupling import TcpSerialCoordinatorCoupling
from automojo.landscaping.coordinators.serial.tcp.tcpserialcoordinator import TcpSerialCoordinator
from automojo.landscaping.services.power.dlipower.dlipowercoordinator import DliPowerCoordinator


class TestFixes(unittest.TestCase):
    def test_dlipower_integration_key(self):
        # Check if DLIPowerServiceCoordinatorCoupling has correct integration attributes
        coupling = DLIPowerServiceCoordinatorCoupling
        print(f"DEBUG: type(coupling) = {type(coupling)}")

        # Should be infrastructure/services/serviceType
        self.assertEqual(coupling.integration_root, "infrastructure")
        self.assertEqual(coupling.integration_section, "services")
        self.assertEqual(coupling.integration_leaf, "serviceType")
        self.assertEqual(coupling.integration_class, "network/power/dli-power")

        # Check if COORDINATOR_TYPE is set
        self.assertEqual(coupling.COORDINATOR_TYPE, DliPowerCoordinator)

    def test_tcpserial_integration_key(self):
        coupling = TcpSerialCoordinatorCoupling
        self.assertEqual(coupling.integration_root, "apod")
        self.assertEqual(coupling.integration_section, "serial")
        self.assertEqual(coupling.integration_leaf, "serialType")
        self.assertEqual(coupling.integration_class, "network/tcpserial")

        # Check if create_coordinator creates TcpSerialCoordinator
        mock_landscape = MagicMock()
        coord = coupling.create_coordinator(mock_landscape)
        self.assertIsInstance(coord, TcpSerialCoordinator)


if __name__ == '__main__':
    unittest.main()
