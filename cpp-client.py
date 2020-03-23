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
import glob
import readline
import os
import getpass

from acumos.c_client.module import OnboardingManager, BundleInformation, ModelInformation


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


class CppClient(object):

    def __init__(self):
        pass

    def read_paths(self, bundle_info):
        bundle_info.model_name = input("name of the model: ")
        print("tab-completion for paths and files is enabled.")
        bundle_info.proto_file = input('path to model.proto: ')
        bundle_info.data_dir = input('path to data directory: ')
        bundle_info.lib_dir = input('path to lib directory: ')
        bundle_info.executable = input('path to executable: ')
        bundle_info.dump_dir = input('name of the dump directory: ')
        if not os.path.isdir(bundle_info.dump_dir):
            os.mkdir(bundle_info.dump_dir)
        return bundle_info

    def _check_hostname(self, model_info):
        if model_info.host_name and str(model_info.port):
            result = input(
                ' ( ' + model_info.host_name + ':' + model_info.port + ' ) Is this a valid hostname and port ? [yes/no]: ')
            if result.lower() == 'no':
                model_info.host_name = input('Enter acumos hostname: ')
                model_info.port = input('Enter acumos port number: ')
                return True
            elif result.lower() == 'yes':
                return True
            else:
                print('Invalid Input : Enter [yes/no]')
                return False
        else:
            model_info.host_name = input('Enter acumos hostname: ')
            model_info.port = input('Enter acumos port number: ')
            return True

    def read_details(self, model_info):
        try:
            model_info.host_name = os.environ['ACUMOS_HOST']
        except KeyError:
            print('Environment variable acumos_hostname does not exist')

        try:
            model_info.port = os.environ['ACUMOS_PORT']
        except KeyError:
            print('Environment variable acumos_port does not exist')

        result = self._check_hostname(model_info)

        while not result:
            result = self._check_hostname(model_info)

        result = input('Do you want to create microservices ? [yes/no]')

        if result.lower() == 'no':
            model_info.create_microservice = False
        elif result.lower() == 'yes':
            model_info.create_microservice = True
        else:
            print('Invalid input : ')

        is_license = input('Do you want to add license ? [yes/no]')

        if is_license.lower() == 'no':
            model_info.license = None
        elif is_license.lower() == 'yes':
            model_info.license = input('path to license file : ')

        model_info.push_api = 'https://' + model_info.host_name + ':' + model_info.port + '/' + model_info.push_api
        model_info.auth_api = 'https://' + model_info.host_name + ':' + model_info.port + '/' + model_info.auth_api

        model_info.user_name = input('User Name: ')
        __Password = getpass.getpass('Password: ')
        model_info.password = __Password
        return model_info


if __name__ == "__main__":

    bundle_information = BundleInformation()
    model_info = ModelInformation()
    completer = PathCompleter()
    cpp_client = CppClient()
    bundle_information = cpp_client.read_paths(bundle_information)
    manager = OnboardingManager()
    manager.create_bundle(bundle_information)
    response = input('Do you want CLI onboarding.? [yes/no]: ')
    if response.lower() == 'yes':
        model_info = cpp_client.read_details(model_info)
        manager.push_model(model_info, bundle_information)
    elif response.lower() == 'no':
        pass
    else:
        print('Invalid Input ')
