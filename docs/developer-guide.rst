.. ===============LICENSE_START=======================================================
.. Acumos CC-BY-4.0
.. ===================================================================================
.. Copyright (C) 2019 Fraunhofer Gesellschaft. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by <YOUR COMPANY NAME>
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..      http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================
.. PLEASE REMEMBER TO UPDATE THE LICENSE ABOVE WITH YOUR COMPANY NAME AND THE CORRECT YEAR
.. this should be very technical, aimed at people who want to help develop the components
.. this should be how the component does what it does, not a requirements document of what the component should do
.. this should contain what language(s) and frameworks are used, with versions
.. this should contain how to obtain the code, where to look at work items (Jira tickets), how to get started developing

.. _developer-guide-template:

=================================
Acumos C++ client Developer Guide
=================================

Overview
========

This developper guide is intended to provide information for developpers who want to contribute to the
acumos-c-client development.

Architecture and Design
=======================

In Acumos a model is packed as a dockerized microservice exposing which is specified using Google protobuf.
In order to achieve that, the modeler must write a short C++ program that attaches the trained model with
the generated gRPC stub in order to build an executable that contains the gRPC webserver as well as the
trained model. This executable will then be started in the docker container.

High-Level Flow
---------------

    .. image:: images/Architecture.png


Class Diagrams
--------------

Class diagramm cpp client

    .. image:: images/Class_diagram_cpp_client.png

Class diagramm run microservice

    .. image:: images/Class_diagramm_run_microservice.png

Sequence Diagrams
-----------------

Sequnce diagramm cpp client


    .. image:: images/Class_diagramm_run_microservice.png
       :scale: 75%

Technology and Frameworks
=========================

#. C++ 11
#. gcc 7.4

Project Resources
=================

Provide gerrit, Jira info,  JavaDoc (javadoc.acumos.org) if relevant, link to REST API documentation, etc.
For example:

- Gerrit repo: acumos-c-client `https://gerrit.acumos.org/r/q/project:acumos-c-client` 
- Jira : `Jira <https://jira.acumos.org>`_  componenent name : acumos-c-client

Development Setup
=================

Classical C++ development environment is required with at least C++ 11 and gcc 7.4

How to Run
==========

Please have a look on Tutorial section of the Acumos C++ Client User Guide

How to Test
===========

A test is available in the user guide

CLI Onboarding
==============

For cli onboarding, you have to set two environment variables **ACUMOS_HOST** and **ACUMOS_PORT**.
In acumos_host you have to write name of your acumos instance. Rest of things for api url is inserted by python script
and your resultant url look like this.

.. code:: python

   Push URL: https://my.acumos.instance.org:443/onboarding-app/v2/models
   Auth URL: https://my.acumos.instance.org:443/onboarding-app/v2/auth


Microservice generation is also dependent on user. You provides the user response to option method.
In cpp cli onboarding, use _push_model because zip model bundle is already created and you have provide
the path to dump directory.

.. code:: python

    option = Options(create_microservice=_create_microservice, license=None)
    session_._push_model(self.dump_dir, self._push_api, self._auth_api, option, 2, None)

