"""
.. module:: upnpcoordinateddevice
   :platform: Darwin, Linux, Unix, Windows
   :synopsis: Module containing the upnpcoordinateddevice functionality.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.interop.protocols.upnp.model.devices.upnprootdevice import UpnpRootDevice

from automojo.interop.protocols.upnp.model.upnpdevicedetail import UpnpDeviceDetail

class UpnpCoordinatedDevice(UpnpRootDevice):

    def __init__(self, device_detail: UpnpDeviceDetail):
        super().__init__(device_detail)

        self._coordinator_ref = None
        return

    