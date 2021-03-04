#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests


def send_set_block_pos(operation_id: str, bc_idx: str, cmd_idx) -> bool:
    json_data = {
        "command": {
            "code": "0x000e",
            "params": [
                {"type": "uint16", "value": bc_idx},
                {"type": "uint8", "value": cmd_idx},
            ],
        }
    }
    response = requests.post(
        "http://localhost:5000/api/operations/{}/cmd".format(operation_id),
        json=json_data,
    ).json()

    return response["ack"]


def send_generate_tlm(operation_id: str, tlm_id: str) -> bool:
    json_data = {
        "command": {
            "code": "0x0021",
            "params": [
                {"type": "uint8", "value": "0x40"},
                {"type": "uint8", "value": tlm_id},
                {"type": "uint8", "value": "1"},
            ],
        }
    }
    response = requests.post(
        "http://localhost:5000/api/operations/{}/cmd".format(operation_id),
        json=json_data,
    ).json()

    return response["ack"]
