#!/usr/bin/env python3
# ===================================================================================
# Copyright (C) 2019 Fraunhofer Gesellschaft. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by Fraunhofer Gesellschaft
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================
import contextlib
import json
import os
import shutil
import subprocess
from os import environ
from zipfile import ZipFile, ZIP_DEFLATED

import acumos.session as session_
import urllib3
from acumos.auth import _USERNAME_VAR, _PASSWORD_VAR
from acumos.metadata import Options

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@contextlib.contextmanager
def _patch_environ(**kwargs):
    '''Temporarily adds kwargs to os.environ'''
    try:
        orig_vars = {k: environ[k] for k in kwargs.keys() if k in environ}
        environ.update(kwargs)
        yield
    finally:
        environ.update(orig_vars)
        for extra_key in (kwargs.keys() - orig_vars.keys()):
            del environ[extra_key]


class BundleInformation(object):

    def __init__(self):
        self.proto_file = ''
        self.data_dir = ''
        self.lib_dir = ''
        self.executable = ''
        self.model_name = ''
        self.dump_dir = ''


class ModelInformation(object):

    def __init__(self):
        self._USER_NAME = ''
        self._PASSWORD = ''
        self.host_name = ''
        self.port = ''
        self.create_microservice = False
        self.license = ''
        self.push_api = "onboarding-app/v2/models"
        self.auth_api = "onboarding-app/v2/auth"


    @property
    def user_name(self):
        return self._USER_NAME

    @user_name.setter
    def user_name(self, user_name):
        self._USER_NAME = user_name

    @property
    def password(self):
        return self._PASSWORD

    @password.setter
    def password(self, password):
        self._PASSWORD = password


class OnboardingManager(object):

    def __init__(self):
        pass

    def create_bundle(self, bundle_info):
        packer = ModelPacker(bundle_info)
        packer.create_model_zip()
        packer.create_meta()
        packer.create_bundle_zip()

    def push_model(self, model_info, bundle_info):
        on_boarding = CLIOnBoarding()
        on_boarding.submit_model(bundle_info, model_info)


class ModelPacker(object):

    def __init__(self, bundle_info):
        self._bundle_info = bundle_info

    def create_model_zip(self):
        print('creating model.zip...', end='', flush=True)
        try:
            with ZipFile(self._bundle_info.dump_dir + '/model.zip', 'w', ZIP_DEFLATED) as zipfile:
                zipfile.write(self._bundle_info.executable, os.path.basename(self._bundle_info.executable))
                self.add_directory(self._bundle_info.lib_dir, 'lib/', zipfile)
                self.add_directory(self._bundle_info.data_dir, 'data/', zipfile)
            print('done.')
        except FileNotFoundError as e:
            print(e)
            quit(1)

    def create_bundle_zip(self):
        bundle_file = self._bundle_info.model_name + '-bundle.zip'
        print('creating ' + bundle_file + '...', end='', flush=True)
        try:
            with ZipFile(self._bundle_info.dump_dir + '/' + bundle_file, 'w', ZIP_DEFLATED) as zipfile:
                zipfile.write(self._bundle_info.dump_dir + '/model.zip', 'model.zip')
                zipfile.write(self._bundle_info.dump_dir + '/model.proto', 'model.proto')
                zipfile.write(self._bundle_info.dump_dir + '/metadata.json', 'metadata.json')
            print('done.')
        except FileNotFoundError as e:
            print(e)
            quit(1)

    def add_directory(self, directory, prefix, zipfile):
        for root, directories, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                zipfile.write(filepath, prefix + filename)

    def create_meta(self):
        print('generating metadata')
        shutil.copy(self._bundle_info.proto_file, self._bundle_info.dump_dir)
        lines = subprocess.getoutput('gcc -v').splitlines()
        gcc_version = lines[-1].split(' ')[2]
        print('target compiler is gcc ' + gcc_version)

        methods = {}
        with open(self._bundle_info.proto_file) as fp:
            for cnt, line in enumerate(fp):
                words = line.strip().split(' ')
                if words[0] == 'rpc':
                    print('adding model method: ' + line)
                    param_input = words[2].strip('(').strip(')')
                    param_output = words[4].strip(';').strip('(').strip(')')
                    rpc = {'input': param_input,
                           'output': param_output,
                           'description': ''}
                    methods[words[1]] = rpc

        meta = {'name': self._bundle_info.model_name,
                'schema': 'acumos.schema.model:0.4.0'}

        runtime = {'version': gcc_version,
                   'encoding': 'protobuf',
                   'name': 'c++',
                   'executable': 'run-microservice'}

        pip = {'indexes': [], 'requirements': []}
        conda = {'channels': [], 'requirements': []}
        dependencies = {'pip': pip, 'conda': conda}
        runtime['dependencies'] = dependencies

        meta['runtime'] = runtime
        meta['methods'] = methods
        with open(self._bundle_info.dump_dir + '/metadata.json', 'w') as mfile:
            json.dump(meta, mfile, indent=2)


class CLIOnBoarding(object):

    def __init__(self):
        pass

    def submit_model(self, bundle_info, model_info):
        # allow users to push using username and password env vars
        with _patch_environ(**{_USERNAME_VAR: model_info.user_name, _PASSWORD_VAR: model_info.password}):
            option = Options(create_microservice=model_info.create_microservice, license=model_info.license)
            session_._push_model(bundle_info.dump_dir, model_info.push_api,  model_info.auth_api, option, 2, None)
