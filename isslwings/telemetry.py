#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests


def get_latest_tlm(operation_id: str, tlm_name: str) -> list:
    response = requests.get(
        "http://localhost:5000/api/operations/{}/tlm".format(operation_id)
    ).json()
    for resp_data in response["data"]:
        if resp_data["packetInfo"]["name"] == tlm_name:
            tlm = resp_data["telemetries"]
    return tlm
