"""
    .. module:: taggingext
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the TaggingExt object.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import TYPE_CHECKING

from  http import HTTPStatus

from automojo.landscaping.services.vmware.vsphere.ext.baseext import BaseExt

if TYPE_CHECKING:
    from automojo.landscaping.services.vmware.vsphere.vsphereagent import VSphereAgent

class TaggingExt(BaseExt):
    """
        Extension that provides access to the vSphere tagging API.
    """

    def __init__(self, agent: "VSphereAgent"):
        """
            Creates a :class:`TaggingExt` extension for a vSphere agent.

            :param agent: Owning :class:`VSphereAgent` instance.
        """
        super().__init__(agent)
        return