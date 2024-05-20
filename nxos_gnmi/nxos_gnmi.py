import sys
import json
import logging
import re
from .templates import Template
from jinja2 import Environment, BaseLoader
from pygnmi.client import gNMIclient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


class NxosGnmi:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        cert: str,
        override: str,
    ):
        self.target = (host, port)
        self.username = username
        self.password = password
        self.cert = cert
        self.client = gNMIclient(
            target=(host, port),
            username=username,
            password=password,
            path_cert=cert,
            override=override,
            debug=True,
        )
        print(self.target)
        self.client.connect()

    def get_xpath(self, paths: list[str]) -> dict:
        return self.client.get(path=paths)

    def set(self, data: list[tuple]) -> dict:
        response = self.client.set(update=data, encoding="json")
        return response  # type: ignore

    def delete_xpath(self, paths: list[str]) -> dict:
        return self.client.set(delete=paths)  # type: ignore


class Nexus(NxosGnmi):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        cert: str,
        override: str,
        config: dict = {},
    ):
        super().__init__(host, port, username, password, cert, override)
        self.config = config
        self.updates = []

    @staticmethod
    def prepare_data(data: dict) -> dict:
        prepared = {}
        attach_groups = {}
        l2vnis = {}
        switches = data["fabric"]["topology"]["switches"]
        networks = data["fabric"]["overlay"]["networks"]
        groups = data["fabric"]["overlay"]["network_attach_groups"]

        # expand network config
        for group in groups:
            name = group["name"]
            switch_group = {}
            for sw in group["switches"]:
                switch_group[str(sw["node_id"])] = {"ports": sw["ports"]}
            attach_groups[name] = switch_group

        for network in networks:
            name = network["name"]
            att_group = network["attach_group"]
            network["attach"] = attach_groups[att_group]
            l2vnis[name] = network

        for sw in switches:
            node_id = sw["node_id"]
            prepared[node_id] = sw
            prepared[node_id]["data"] = {
                "networks": {},
                "interfaces": {},
            }
            for name, config in l2vnis.items():
                if config["attach"].get(str(node_id)) is None:
                    continue
                prepared[node_id]["data"]["networks"][name] = config
                prepared[node_id]["data"]["networks"][name]["ports"] = config[
                    "attach"
                ].get(str(node_id))["ports"]

        for node_id, config in prepared.items():
            for _, net_config in config["data"]["networks"].items():
                for intf in net_config["ports"]:
                    intf_config = prepared[node_id]["data"]["interfaces"].get(intf)
                    if intf_config is None:
                        r_intf = r"(eth).*(\d+\/\d{1,2})"
                        result = re.match(r_intf, intf, re.I)
                        if result is None:
                            continue  # type: ignore
                        s_intf_name = result.group(1).lower() + result.group(2)
                        prepared[node_id]["data"]["interfaces"][intf] = {
                            "name": s_intf_name,
                            "trunk_allowed_vlan": [net_config["vlan_id"]],
                        }
                    else:
                        prepared[node_id]["data"]["interfaces"][intf][
                            "trunk_allowed_vlan"
                        ].append(net_config["vlan_id"])

        return prepared

    def _render_update(self, template: dict, item: dict) -> tuple[str, dict]:
        prefix = template.get("prefix")
        update_template = template.get("update_template")
        if prefix is None or update_template is None:
            logger.error(f"template defination is wrong: {template}")

        rtemplate = Environment(loader=BaseLoader).from_string(update_template)  # type: ignore
        data = rtemplate.render(**item)
        return (prefix, json.loads(data))  # type: ignore

    def render_update(self):
        for _, network in self.config["data"]["networks"].items():
            update = self._render_update(Template.BD, network)
            self.updates.append(update)

            update = self._render_update(Template.SVI, network)
            self.updates.append(update)

            update = self._render_update(Template.NVE, network)
            self.updates.append(update)

            update = self._render_update(Template.EVPN, network)
            self.updates.append(update)

        for _, intf in self.config["data"]["interfaces"].items():
            update = self._render_update(Template.INTF, intf)
            self.updates.append(update)

    def send(self):
        if self.updates == []:
            return
        self.set(data=self.updates)

    def get(self, paths: list[str]) -> dict:
        return self.client.get(paths)  # type: ignore
