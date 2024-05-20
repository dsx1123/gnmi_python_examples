import yaml
import argparse
from jinja2 import Template

robot_template = "vxlan.robot.j2"
robot_test_file = "vxlan.robot"
testbed_template = "testbed.yaml.j2"
testbeds_folder = "./testbeds"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", help="envrionment")
    args = parser.parse_args()
    env = args.env
    data = {
        "devices": [],
        "vni_list": [],
        "env": env
    }

    with open(f"../env/{env}/topology.yaml", "r") as file:
        fabric = yaml.safe_load(file)
        topology = fabric["fabric"]["topology"]["switches"]

    with open("../config/config.yaml", "r") as file:
        fabric = yaml.safe_load(file)
        networks = fabric["fabric"]["overlay"]["networks"]

    for device in topology:
        if device["role"] != "leaf":
            continue
        data["devices"].append(
            {
                "name": device["name"],
                "ip": device["management_ipv4_address"],
            }
        )

    data["vni_list"] = [n["vni"] for n in networks]

    with open(robot_template) as file:
        template = Template(file.read())

    rendered = template.render(data)
    with open(robot_test_file, "w") as file:
        file.write(rendered)

    with open(testbed_template) as file:
        template = Template(file.read())

    rendered = template.render(data)
    with open(f"{testbeds_folder}/{env}.yaml", "w") as file:
        file.write(rendered)


if __name__ == "__main__":
    main()
