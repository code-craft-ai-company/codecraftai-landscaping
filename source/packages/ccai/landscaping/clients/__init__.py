"""
    .. module:: clients
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Package initialization for the clients package.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

# Extension distributions ship their own ``ccai/landscaping/clients/<kind>`` packages (interop-ext-tasker
# ships ``clients/taskers``). Merging every ``clients`` directory on the namespace path keeps those
# importable when the extension is not installed into the same directory as this package.
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
