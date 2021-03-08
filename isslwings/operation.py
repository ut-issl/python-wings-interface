#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests


class Operation:
    def __init__(self, operation_idx: int, url: str = "http://localhost:5000"):
        self.url = url

        response = requests.get("{}/api/operations".format(self.url)).json()
        self.operation_id = response["data"][operation_idx]["id"]

    def send_set_block_pos(self, bc_idx: str, cmd_idx) -> bool:
        cmd_code = "0x000e"
        cmd_params = [
            {"type": "uint16", "value": bc_idx},
            {"type": "uint8", "value": cmd_idx},
        ]
        return self._send_cmd(cmd_code, cmd_params)

    def send_generate_tlm(self, tlm_id: str) -> bool:
        cmd_code = "0x0021"
        cmd_params = [
            {"type": "uint8", "value": "0x40"},
            {"type": "uint8", "value": tlm_id},
            {"type": "uint8", "value": "1"},
        ]
        return self._send_cmd(cmd_code, cmd_params)

    def get_latest_tlm(self, tlm_name: str) -> list:
        response = requests.get(
            "{}/api/operations/{}/tlm".format(self.url, self.operation_id)
        ).json()
        for resp_data in response["data"]:
            if resp_data["packetInfo"]["name"] == tlm_name:
                tlm = resp_data["telemetries"]
        return tlm

    def _send_cmd(self, cmd_code: str, cmd_params: list) -> bool:
        json_data = {"command": {"code": cmd_code, "params": cmd_params}}
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json=json_data,
        ).json()

        return response["ack"]
