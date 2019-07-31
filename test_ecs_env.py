from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
import json
from unittest import TestCase
import ecs_env_file
from unittest import mock
from shutil import copyfile
import os
from copy import deepcopy

def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    # raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


@mock.patch.object(basic.AnsibleModule, "exit_json", exit_json)
@mock.patch.object(basic.AnsibleModule, "fail_json", fail_json)
class Testing(TestCase):

    def setUp(self) -> None:
        self.test_file = "./ecs_containers.template.test.json"

        # ensure test file does not exist
        self.tearDown()

        copyfile("./ecs_containers.template.json", self.test_file)

        self.base_one_env = "base.env"
        self.base_two_env = "base2.env"

        self.required_parameters = {
            "env_files": [
                self.base_one_env,
                self.base_two_env
            ],
            "cloud_formation_file": self.test_file
        }

        self.base_one = {
            "name": "bar",
            "env": "stage"
        }

        self.base_two = {
            "env": "staging",
            "new_env": "bar"
        }

        self.all_env = {}
        self.all_env.update(self.base_one)
        self.all_env.update(self.base_two)

    def compare_env(self, expected_dict, actual_list):
        self.assertEqual(len(expected_dict), len(actual_list))

        for i in actual_list:
            self.assertEqual(i["Value"], expected_dict.get(i["Name"]))

    def compare_all_containers(self, containers, env):
        for container in containers:
            self.compare_env(env, container['Environment'])

    def compare_file(self, file, env):
        self.compare_all_containers(self.get_container_definitions(file), env)

    def get_container_definitions(self, test_file=None):
        if test_file is None:
            test_file = self.test_file

        with open(test_file) as json_file:
            data = json.load(json_file)

        return data["Resources"]["TaskDefinition"]\
                ["Properties"]["ContainerDefinitions"]

    def force_delete_file(self, file):
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

    def tearDown(self) -> None:
        self.force_delete_file(self.test_file)

    def test_missing_parameters(self):

        for param in ("env_files", "cloud_formation_file"):
            parameters = deepcopy(self.required_parameters)

            del parameters[param]

            set_module_args(parameters)

            self.assertRaises(AnsibleFailJson, ecs_env_file.main)

    def test_happy_case(self):

        set_module_args(self.required_parameters)
        ecs_env_file.main()

        self.compare_file(self.test_file, self.all_env)

    def test_setting_on_one_container_only(self):
        parameters = deepcopy(self.required_parameters)
        parameters["container_name"] = "bar"

        set_module_args(parameters)
        ecs_env_file.main()

        containers = self.get_container_definitions()

        for container in containers:
            if container['Name'] == 'bar':
                env = container.get('Environment')
                self.compare_env(self.all_env, env)
            else:
                env = container.get('Environment', {})
                self.compare_env({}, env)

    def test_setting_one_file_only(self):
        parameters = deepcopy(self.required_parameters)
        parameters['env_files'] = [self.base_two_env]
        set_module_args(parameters)
        ecs_env_file.main()

        self.compare_file(self.test_file, self.base_two)

    def test_setting_output_another_file(self):
        new_test_file = self.test_file + "dest.json"
        # ensure file does not exist
        self.force_delete_file(new_test_file)

        parameters = deepcopy(self.required_parameters)
        parameters['destination'] = new_test_file

        set_module_args(parameters)
        ecs_env_file.main()

        self.compare_file(new_test_file, self.all_env)

        self.force_delete_file(new_test_file)









