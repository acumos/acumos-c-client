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

from acumos_cpp.c_client.module import OnboardingManager, BundleInformation, ModelInformation

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
    response = None
    result = None
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

    def _check_userinput(self, result):
        if result.lower() == 'yes':
            return True
        elif result.lower() == 'no':
            return True
        else:
            return False

    def read_microserviceinput(self):
        self.response = input('Do you want to create microservice ? [yes/no]: ')
        self.result = self._check_userinput(self.response)
        if not self.result:
            print("Invalid Input: Please enter yes/no")
            self.response = self.read_microserviceinput()
        return self.response

    def read_deploy_input(self):
        self.response = input('Do you want to deploy the microservice ? [yes/no]: ')
        self.result = self._check_userinput(self.response)
        if not self.result:
            print("Invalid Input: Please enter yes/no")
            self.response = self.read_deploy_input()
        return self.response

    def read_licenseinput(self):
        self.response = input('Do you want to add license ? [yes/no]: ')
        self.result = self._check_userinput(self.response)
        if not self.result:
            print("Invalid Input: Please enter yes/no")
            self.response = self.read_licenseinput()
        return self.response

    def read_details(self, model_info):
        try:
            model_info.host_name = os.environ['ACUMOS_HOST']
        except KeyError:
            print('Environment variable ACUMOS_HOST does not exist')

        try:
            model_info.port = os.environ['ACUMOS_PORT']
        except KeyError:
            print('Environment variable ACUMOS_PORT does not exist')

        result = self._check_hostname(model_info)

        while not result:
            result = self._check_hostname(model_info)


        response = self.read_microserviceinput()
        if response.lower() == 'no':
            model_info.create_microservice = False
        elif response.lower() == 'yes':
            model_info.create_microservice = True
        else:
            print('Invalid Input : ')

        response = self.read_deploy_input()
        if response.lower() == 'no':
            model_info.deploy = False
        elif response.lower() == 'yes':
            model_info.deploy = True
        else:
            print('Invalid Input : ')

        is_license = self.read_licenseinput()

        if is_license.lower() == 'no':
            model_info.license = None
        elif is_license.lower() == 'yes':
            model_info.license = input('path to license file : ')
        else:
            print('Invalid Input : ')

        model_info.push_api = 'https://' + model_info.host_name + ':' + model_info.port + '/' + model_info.push_api
        model_info.auth_api = 'https://' + model_info.host_name + ':' + model_info.port + '/' + model_info.auth_api

        # format of ACUMOS_TOKEN is 'username:API_TOKEN'
        try:
            model_info.api_token = os.environ['ACUMOS_TOKEN']
        except KeyError:
            print('Environment variable ACUMOS_TOKEN does not exist, using JWT authentication instead')
            model_info.user_name = input('User Name: ')
            __Password = getpass.getpass('Password: ')
            model_info.password = __Password

        return model_info

class Checkinput(object):
    result = None
    response = None

    def __init__(self):
        pass

    def _check_userinput(self,response):
        if response.lower() == 'yes':
            return True
        elif response.lower() == 'no':
            return True
        else:
            return False

    def read_userinput(self):
        self.response = input('Do you want CLI onboarding.? [yes/no]: ')
        self.result = self._check_userinput(self.response)

        if not self.result:
            print('Invalid Input: Please enter yes/no')
            self.response = self.read_userinput()

        return self.response


if __name__ == "__main__":

    bundle_information = BundleInformation()
    model_info = ModelInformation()
    completer = PathCompleter()
    cpp_client = CppClient()
    check_input = Checkinput()
    bundle_information = cpp_client.read_paths(bundle_information)
    manager = OnboardingManager()
    manager.create_bundle(bundle_information)

    response = check_input.read_userinput()

    if response.lower() == 'yes':
        model_info = cpp_client.read_details(model_info)
        manager.push_model(model_info, bundle_information)
    elif response.lower() == 'no':
        print('Your Acumos model bundle has been created in ' +
             bundle_information.dump_dir + ', you can use it to onboard by Web your model in Acumos and its path is : ' + os.getcwd() + '/' + bundle_information.dump_dir)
    else:
        print('Invalid Input ')
