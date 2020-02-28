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
import os
import readline
import getpass
import glob
import shutil
import subprocess
import json
from zipfile import ZipFile, ZIP_DEFLATED
import contextlib
from os import environ
from acumos.auth import _USERNAME_VAR, _PASSWORD_VAR
from acumos.metadata import Options
import acumos.session as session_
import urllib3

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


class PathCompleter(object):

    def __init__(self):
        readline.set_completer_delims('\t')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete_path)

    def complete_path(self, text, state):
        # autocomplete directories with having a trailing slash
        return [self._add_slash(x) for x in glob.glob(text + '*')][state]

    def _add_slash(self, text):
        if os.path.isdir(text):
            return text + '/'
        else:
            return text


class ModelPacker(object):

    def __init__(self):
        self.proto_file = ''
        self.data_dir = ''
        self.lib_dir = ''
        self.executable = ''
        self.model_name = ''
        self.dump_dir = ''

    def read_paths(self):
        self.model_name = input("name of the model: ")
        print("tab-completion for paths and files is enabled.")
        self.proto_file = input('path to model.proto: ')
        self.data_dir = input('path to data directory: ')
        self.lib_dir = input('path to lib directory: ')
        self.executable = input('path to executable: ')
        self.dump_dir = input('name of the dump directory: ')
        if not os.path.isdir(self.dump_dir):
            os.mkdir(self.dump_dir)

    def create_model_zip(self):
        print('creating model.zip...', end='', flush=True)
        try:
            with ZipFile(self.dump_dir+'/model.zip', 'w', ZIP_DEFLATED) as zipfile:
                zipfile.write(self.executable, os.path.basename(self.executable))
                self.add_directory(self.lib_dir, 'lib/', zipfile)
                self.add_directory(self.data_dir, 'data/', zipfile)
            print('done.')
        except FileNotFoundError as e:
            print(e)
            quit(1)

    def create_bundle_zip(self):
        bundle_file = self.model_name + '-bundle.zip'
        print('creating ' + bundle_file + '...', end='', flush=True)
        try:
            with ZipFile(self.dump_dir+'/' + bundle_file, 'w', ZIP_DEFLATED) as zipfile:
                zipfile.write(self.dump_dir+'/model.zip', 'model.zip')
                zipfile.write(self.dump_dir+'/model.proto', 'model.proto')
                zipfile.write(self.dump_dir+'/metadata.json', 'metadata.json')
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
        shutil.copy(self.proto_file, self.dump_dir)
        lines = subprocess.getoutput('gcc -v').splitlines()
        gcc_version = lines[-1].split(' ')[2]
        print('target compiler is gcc ' + gcc_version)

        methods = {}
        with open(self.proto_file) as fp:
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

        meta = {'name': self.model_name,
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
        with open(self.dump_dir+'/metadata.json', 'w') as mfile:
            json.dump(meta, mfile, indent=2)


class CLIOnBoarding(object):
    def __init__(self):

        self._USER_NAME = ''
        self._PASSWORD = ''
        self._host_name = ''
        self._port = ''
        self._create_microservice = False
        self._push_api = "onboarding-app/v2/models"
        self._auth_api = "onboarding-app/v2/auth"

    def check_hostname(self):
        if self._host_name and str(self._port):
            result = input(
                ' ( ' + self._host_name + ':' + self._port + ' ) Is this a valid hostname and port ? [yes/no]: ')
            if result.lower() == 'no':
                self._host_name = input('Enter acumos hostname: ')
                self._port = input('Enter acumos port number: ')
                return True
            elif result.lower() == 'yes':
                return True
            else:
                print('Invalid Input : Enter [yes/no]')
                return False
        else:
            self._host_name = input('Enter acumos hostname: ')
            self._port = input('Enter acumos port number: ')
            return True

    def read_details(self):
        try:
            self._host_name = os.environ['ACUMOS_HOST']
        except KeyError:
            print('Environment variable acumos_hostname does not exist')

        try:
            self._port = os.environ['ACUMOS_PORT']
        except KeyError:
            print('Environment variable acumos_port does not exist')

        result = self.check_hostname()

        while not result:
            result = self.check_hostname()

        result = input('Do you want to create microservices ? [yes/no]')

        if result.lower() == 'no':
            self._create_microservice = False
        elif result.lower() == 'yes':
            self._create_microservice = True
        else:
            print('Invalid input : ')

        self._push_api = 'https://' + self._host_name + ':' + self._port + '/' + self._push_api
        self._auth_api = 'https://' + self._host_name + ':' + self._port + '/' + self._auth_api

        self._USER_NAME = input('User Name: ')
        self._PASSWORD = getpass.getpass('Password: ')

    def test_session(self, dump_dir):
        # allow users to push using username and password env vars
        with _patch_environ(**{_USERNAME_VAR: self._USER_NAME, _PASSWORD_VAR: self._PASSWORD}):
            option = Options(create_microservice=self._create_microservice, license=None)
            session_._push_model(dump_dir, self._push_api, self._auth_api, option, 2, None)


if __name__ == "__main__":
    completer = PathCompleter()
    packer = ModelPacker()
    packer.read_paths()
    packer.create_model_zip()
    packer.create_meta()
    packer.create_bundle_zip()
    response = input('Do you want CLI onboarding.? [yes/no]: ')
    if response.lower() == 'yes':
        cli = CLIOnBoarding()
        cli.read_details()
        cli.test_session(packer.dump_dir)
    elif response.lower() == 'no':
        print('')
    else:
        print('Invalid Input ')
