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
Provides a Acumos session for pushing and dumping models
"""
import random
import string
import shutil
import json
import requests
import fnmatch
import warnings
from contextlib import contextmanager, ExitStack
from tempfile import TemporaryDirectory
from os import walk, mkdir
from os.path import extsep, exists, abspath, dirname, isdir, isfile, expanduser, relpath, basename, join as path_join
from pathlib import Path
from collections import namedtuple
from glob import glob

from acumos.metadata import Options
from acumos.utils import dump_artifact
from acumos.exc import AcumosError
from acumos.logging import get_logger
from acumos.auth import get_jwt, clear_jwt

logger = get_logger(__name__)

_LICENSE_NAME = 'license.json'
_PYEXT = "{}py".format(extsep)
_PYGLOB = "*{}".format(_PYEXT)

_ServerResponse = namedtuple('ServerResponse', 'status_code reason text')
_DEPR_MSG = ('Usage of `auth_api` is deprecated; provide an onboarding token instead. '
             'See https://pypi.org/project/acumos/ for more information.')


class AcumosSession(object):
    '''
    A session that enables onboarding models to Acumos

    Parameters
    ----------
    push_api : str
        The full URL to the Acumos onboarding server upload API
    auth_api : str
        The full URL to the Acumos onboarding server authentication API.

        .. deprecated:: 0.7.1
            Users should provide an onboarding token instead of username and password credentials.
    '''

    def __init__(self, push_api=None, auth_api=None):
        self.push_api = push_api
        self.auth_api = auth_api

        if auth_api is not None:
            warnings.warn(_DEPR_MSG, DeprecationWarning, stacklevel=2)


def _validate_options(options):
    '''Validates and returns an `Options` object'''
    if options is None:
        options = Options()
    elif not isinstance(options, Options):
        raise AcumosError('The `options` parameter must be of type `acumos.metadata.Options`')
    return options


def _assert_valid_api(param, api, required):
    '''Raises AcumosError if an api is invalid'''
    if api is None:
        if required:
            raise AcumosError("AcumosSession.push requires that the API for `{}` be provided".format(param))
    else:
        if not api.startswith('https'):
            logger.warning(
                "Provided `{}` API {} does not begin with 'https'. Your password and token are visible in plaintext!".format(
                    param, api))


def _push_model(dump_dir, push_api, auth_api, options, max_tries=2, extra_headers=None):
    '''Pushes a model to the Acumos server'''
    with ExitStack() as stack:
        model = stack.enter_context(open(path_join(dump_dir, 'model.zip'), 'rb'))
        meta = stack.enter_context(open(path_join(dump_dir, 'metadata.json')))
        proto = stack.enter_context(open(path_join(dump_dir, 'model.proto')))

        files = {'model': ('model.zip', model, 'application/zip'),
                 'metadata': ('metadata.json', meta, 'application/json'),
                 'schema': ('model.proto', proto, 'text/plain')}

        # include a license if one is provided
        if options.license is not None:
            _add_license(dump_dir, options.license)
            license = stack.enter_context(open(path_join(dump_dir, _LICENSE_NAME)))
            files['license'] = (_LICENSE_NAME, license, 'application/json')

        tries = 1
        _post_model(files, push_api, auth_api, tries, max_tries, extra_headers, options)


def _add_license(rootdir, license_str):
    '''Adds a license file to the model root directory'''
    license_dst = path_join(rootdir, _LICENSE_NAME)
    if isfile(license_str):
        shutil.copy(license_str, license_dst)
    else:
        license_dict = {'license': license_str}  # the license team hasn't defined a license schema yet
        dump_artifact(license_dst, data=license_dict, module=json, mode='w')


def _post_model(files, push_api, auth_api, tries, max_tries, extra_headers, options):
    '''Attempts to post the model to Acumos'''
    headers = {'Authorization': get_jwt(auth_api),
               'isCreateMicroservice': 'true' if options.create_microservice else 'false'}
    if extra_headers is not None:
        headers.update(extra_headers)

    resp = requests.post(push_api, files=files, headers=headers, verify=False)

    if resp.ok:
        response = resp.json()
        print(options.create_microservice)
        try:
            if options.create_microservice:
                logger.info("Model pushed successfully to {} model URI {} ".format(push_api, response['dockerImageUri']))
            else:
                logger.info("Model pushed successfully to {} ".format(push_api))
        except KeyError:
            logger.info("Model pushed successfully to {} ".format(push_api))
    else:
        clear_jwt()
        if resp.status_code == 401 and tries != max_tries:
            logger.warning('Model push failed due to an authorization failure. Clearing credentials and trying again')
            _post_model(files, push_api, auth_api, tries + 1, max_tries, extra_headers, options)
        else:
            raise AcumosError("Model push failed: {}".format(_ServerResponse(resp.status_code, resp.reason, resp.text)))
