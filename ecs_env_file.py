from ansible.module_utils.basic import AnsibleModule

import json
import os

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None


def main():

    module = AnsibleModule(
        argument_spec=dict(
            env_files=dict(required=True, type='list'),
            cloud_formation_file=dict(required=True),
            container_name=dict(required=False),
            destination=dict(required=False),
        ),
        supports_check_mode=True,
    )

    if dotenv_values is None:
        module.fail_json(msg='parse_dotenv module is not available')

    env_file = module.params['env_files']
    cloud_formation_file = module.params['cloud_formation_file']
    container_name = module.params.get('container_name')
    destination = module.params.get('destination')

    destination = cloud_formation_file if destination is None else destination

    envs = dict()
    for i in env_file:
        if not os.path.isfile(i):
            module.fail_json(msg="File {} does not exist".format(i))
        for key, value in dotenv_values(i).items():
            envs[key] = value
    ecs_env = []
    for key, value in envs.items():
        ecs_env.append({"Name": key, "Value": value})

    with open(cloud_formation_file) as json_file:
        data = json.load(json_file)

    container_definitions = data["Resources"]["TaskDefinition"]["Properties"]["ContainerDefinitions"]

    for container in container_definitions:
        if container_name is None or container["Name"] == container_name:
            # check if Environment hs
            if not container.get("Environment"):
                container['Environment'] = []
            container['Environment'].extend(ecs_env)

    with open(destination, "w") as f:
        json.dump(data, f, indent=4)

    module.exit_json(changed=True,
                     result="done")


if __name__ == '__main__':
    main()