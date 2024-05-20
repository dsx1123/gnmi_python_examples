import os
import sys
import logging
import argparse

from nxos_gnmi.nxos_gnmi import Nexus
from nxos_gnmi.verify import FabricValidator


logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


schema = "fabric.yaml"
cert = "./cert/gnmi.crt"
grpc_port = 50050


def validate(env: str) -> tuple[bool, dict]:
    """
    validate input against schema

    :param env: deploy envrionment
    :return: validated(bool), consolidated data(dict)
    """
    validator = FabricValidator(os.path.abspath(f"./schemas/{schema}"), "")
    validated, data = validator.validate_syntax(os.path.abspath("./"), env)
    if not validated:
        exit(2)
    return validated, data


def deploy(username: str, password: str, data: dict):
    """
    deployg configuration

    :param username: nxos username
    :param password: nxos password
    :param data: validated data
    """
    deploy_instances = []
    prepared_data = Nexus.prepare_data(data)
    for _, config in prepared_data.items():
        nx = Nexus(
            config["management_ipv4_address"],
            grpc_port,
            username,
            password,
            cert,
            "gnmi",
            config,
        )
        deploy_instances.append(nx)
        nx.render_update()
        nx.send()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="action", choices=["validate", "deploy"])
    parser.add_argument("-e", "--env", help="deploy envrionment", default="stage")
    args = parser.parse_args()

    username = os.getenv("switch_username")
    password = os.getenv("switch_password")
    if username is None or password is None:
        logger.error("Please set ENV switch_username and switch_password")
        exit(-11)

    # validate the input data  against schema
    if args.action == "validate":
        validate(args.env)
    if args.action == "deploy":
        _, data = validate(args.env)
        deploy(username, password, data)


if __name__ == "__main__":
    main()
