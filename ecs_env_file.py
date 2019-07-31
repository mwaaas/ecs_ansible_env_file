from ansible.module_utils.basic import AnsibleModule
from py_dotenv.dotenv import parse_dotenv

import json

try:
    import jsonpointer
except ImportError:
    jsonpointer = None


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

    if jsonpointer is None:
        module.fail_json(msg='jsonpointer module is not available')

    env_file = module.params['env_files']
    cloud_formation_file = module.params['cloud_formation_file']
    container_name = module.params.get('container_name')
    destination = module.params.get('destination')

    destination = cloud_formation_file if destination is None else destination

    envs = dict()
    for i in env_file:
        for key, value in parse_dotenv(i):
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
                     result=data)


if __name__ == '__main__':
    main()