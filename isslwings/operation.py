#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from .telemetry import Telemetry


class Operation:
    def __init__(self, operation_idx: int, url: str = "http://localhost:5000"):
        self.url = url

        response = requests.get("{}/api/operations".format(self.url)).json()
        self.operation_id = response["data"][operation_idx]["id"]

    def send_set_block_pos(self, bc_idx: int, cmd_idx: int) -> None:
        cmd_code = "0x000e"
        cmd_params = [
            {"type": "uint16", "value": str(bc_idx)},
            {"type": "uint8", "value": str(cmd_idx)},
        ]
        self._send_cmd(cmd_code, cmd_params)

    def send_generate_tlm(self, tlm_id: int) -> None:
        cmd_code = "0x0021"
        cmd_params = [
            {"type": "uint8", "value": "0x40"},
            {"type": "uint8", "value": str(tlm_id)},
            {"type": "uint8", "value": "1"},
        ]
        self._send_cmd(cmd_code, cmd_params)

    def get_latest_tlm(self, tlm_code_name: str) -> Telemetry:
        response = requests.get(
            "{}/api/operations/{}/tlm".format(self.url, self.operation_id)
        ).json()
        return Telemetry(tlm_code_name, response)

    def _send_cmd(self, cmd_code: str, cmd_params: list) -> None:
        json_data = {"command": {"code": cmd_code, "params": cmd_params}}
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json=json_data,
        ).json()

        if response["ack"] == False:
            raise Exception(
                "An error has occured while sending command ID={}".format(cmd_code)
            )
