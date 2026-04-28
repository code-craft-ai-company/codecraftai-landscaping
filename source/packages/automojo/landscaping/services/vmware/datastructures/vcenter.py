"""
    .. module:: vcenter
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Backwards-compatible re-export of vCenter summary dataclasses.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>

    Historical context: ``DatacenterSummary`` and ``FolderSummary`` were originally
    declared here AND in ``model/summary.py`` as separate but field-identical
    dataclasses.  Two distinct classes with the same name produced silent type
    drift at the boundary between modules that imported from one path versus the
    other (e.g. ``isinstance`` checks across the boundary failed).  The
    ``model/summary.py`` module is the canonical home — it also declares
    ``VmSummary`` and is the import target for the richer extension module.
    This module now re-exports those classes from the canonical home so that
    every existing call site continues to work and every reference resolves to
    the same class object.
"""


__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.landscaping.services.vmware.datastructures.model.summary import (
    DatacenterSummary,
    FolderSummary,
)


__all__ = [
    "DatacenterSummary",
    "FolderSummary",
]
