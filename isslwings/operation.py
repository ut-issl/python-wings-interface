#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .telemetry import Telemetry


class Operation:
    def __init__(self, operation_idx: int, url: str = "http://localhost:5000"):
        self.url = url

        response = requests.get("{}/api/operations".format(self.url)).json()
        self.operation_id = response["data"][operation_idx]["id"]

    def get_latest_tlm(self, tlm_code_name: str) -> Telemetry:
        response = requests.get(
            "{}/api/operations/{}/tlm".format(self.url, self.operation_id)
        ).json()
        return Telemetry(tlm_code_name, response)

    def send_cmd(self, cmd_name, cmd_params_value) -> None:
        response = requests.get(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id)
        ).json()

        for command in response["data"]:
            if command["name"] != cmd_name:
                continue

            command_to_send = {"code": command["code"], "params": []}

            for i in range(len(command["params"])):
                command_to_send["params"].append(
                    {
                        "type": command["params"][i]["type"][:-2],
                        "value": str(cmd_params_value[i]),
                    }
                )
            self._send_cmd(command_to_send)
            return

        raise Exception('Command name "{}" cannot be found.'.format(cmd_name))

    def _send_cmd(self, command: dict) -> None:
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
        ).json()

        if response["ack"] == False:
            raise Exception(
                'An error has occured while sending command "{}"'.format(command)
            )

    def get_cmd_id(self, cmd_name: str) -> int:
        response = requests.get(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id)
        ).json()
        for cmd_info in response["data"]:
            if cmd_info["name"] == cmd_name:
                return int(cmd_info["code"], 16)

        raise Exception('Command name "{}" cannot be found.'.format(cmd_name))
