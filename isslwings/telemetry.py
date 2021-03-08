#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Telemetry:
    def __init__(self, tlm_code_name: str, response: dict):
        self.tlm_code_name = tlm_code_name

        for response_data in response["data"]:
            if response_data["packetInfo"]["name"] == self.tlm_code_name:
                self.tlm_data = response_data["telemetries"]
                return

        raise Exception(
            'Telemetry code name "{}" cannot be found.'.format(tlm_code_name)
        )

    def __getitem__(self, tlm_name: str) -> dict:
        for tlm_element in self.tlm_data:
            if tlm_element["name"] == "{}.{}".format(self.tlm_code_name, tlm_name):
                return tlm_element["value"]

        raise Exception(
            'Telemetry name "{}" cannot be found in "{}".'.format(
                tlm_name, self.tlm_code_name
            )
        )
