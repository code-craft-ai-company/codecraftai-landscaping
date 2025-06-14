"""
    .. module:: baseext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the BaseExt object used share common functionality between vshere agent extensions.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

import weakref


if TYPE_CHECKING:
    from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent

class BaseExt:

    def __init__(self, agent: "VSphereAgent"):
        """
            Creates a base extension bound to a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        self._agent_ref = weakref.ref(agent)
        return
    
    @property
    def agent(self) -> "VSphereAgent":
        """
            Returns the owning :class:`VSphereAgent` instance.

            :returns: Agent instance associated with this extension.
            :rtype: VSphereAgent
        """
        return self._agent_ref()
