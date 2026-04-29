============================
Automation Mojo Landscaping
============================

The ``automojo-landscaping`` package provides the topology model and device-discovery framework that automojo tests and automation tools use to reason about the machines, clusters, and services under test. A ``Landscape`` aggregates the devices declared by configuration, organises them through integration layers, and exposes them through friendly identifiers so that tests can address resources by role rather than by raw hostnames or IP addresses. It builds on ``automojo-interfaces``, ``automojo-interop``, and ``automojo-credentials``, and is typically consumed by higher-level orchestration packages.

Highlights
==========

- ``AutomationPod`` as the configuration-coupled entry point to the global ``Landscape``.
- ``CoordinatorCoupling`` subclasses that attach protocol- or service-specific coordinators (SSH, serial, VMware vSphere, DLI power, Raspberry Pi clusters, and more).
- Client, service, and cluster base classes under ``clients/``, ``services/``, and ``clusters/`` representing managed devices.
- Pluggable coordinators for discovering and wiring devices of a given type.
- Extension hooks under ``extensions/`` for downstream packages such as ``automojo-interop-ext-upnp`` and ``automojo-interop-ext-tasker``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/`` - Package source code.
- ``source/testroots/automojo/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation.
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-envrionment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run the single-host test suite:

.. code-block:: bash

   testbase testing run --root source/testroots/automojo --includes=automojo.tests.landscaping.singlehost --output=./.output

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
- Design documentation: ``specs/design.md``
- Requirements: ``specs/requirements.md``
