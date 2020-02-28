# -*- coding: utf-8 -*-
# ===============LICENSE_START=======================================================
# Acumos Apache-2.0
# ===================================================================================
# Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by AT&T and Tech Mahindra
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================
"""
Provides metadata generation utilities
"""

import sys

BUILTIN_MODULE_NAMES = set(sys.builtin_module_names)
PACKAGE_DIRS = {'site-packages', 'dist-packages'}
SCHEMA_VERSION = '0.4.0'
_SCHEMA = "acumos.schema.model:{}".format(SCHEMA_VERSION)

# known package mappings because Python packaging is madness
_REQ_MAP = {
    'sklearn': 'scikit-learn',
}


class Options(object):
    '''
    A collection of options that users may wish to specify along with their Acumos model

    Parameters
    ----------
    create_microservice : bool, optional
        If True, instructs the Acumos platform to eagerly build the model microservice
    license : str, optional
        A license to include with the Acumos model. This parameter may either be a path to a license
        file, or a string containing the license content.
    '''
    __slots__ = ('create_microservice', 'license')

    def __init__(self, create_microservice=True, license=None):
        self.create_microservice = create_microservice
        self.license = license
