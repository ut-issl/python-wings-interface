#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import requests


class Operation:
    def __init__(self, operation_idx: int = 0, url: str = "http://localhost:5000"):
        self.url = url

        response = requests.get("{}/api/operations".format(self.url)).json()

        if not response["data"]:
            raise Exception("Operations don't exist.")

        self.operation_id = response["data"][operation_idx]["id"]

    def get_latest_tlm(self, tlm_code_name: str) -> dict:
        response = requests.get(
            "{}/api/operations/{}/tlm".format(self.url, self.operation_id)
        ).json()

        if not response["data"]:
            raise Exception("Telemetries are not stored.")

        # 該当するtlm_code_nameのテレメ情報を探す
        tlm_code_is_found = False
        for response_data in response["data"]:
            if response_data["packetInfo"]["name"] == tlm_code_name:
                tlm_code_is_found = True
                break

        if not tlm_code_is_found:
            raise Exception(
                'Telemetry code name "{}" cannot be found.'.format(tlm_code_name)
            )

        telemetry_data = {}
        telemetries = response_data["telemetries"]

        for telemetry in telemetries:

            # TODO: テレメデータがない時の例外処理を加える

            # strで読み込んでしまっているので、適切な型へcastする
            if telemetry["type"] in [
                "int8_t",
                "uint8_t",
                "int16_t",
                "uint16_t",
                "int32_t",
                "uint32_t",
            ]:
                data = int(telemetry["value"])
            elif telemetry["type"] in ["float", "double"]:
                data = float(telemetry["value"])
            else:
                data = telemetry["value"]

            telemetry_data[re.sub(tlm_code_name + ".", "", telemetry["name"])] = data

        return telemetry_data

    def send_cmd(self, cmd_code: int, cmd_params_value: tuple) -> None:
        response = requests.get(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id)
        ).json()

        if not response["data"]:
            raise Exception("An error has occurred while fetching cmd data.")

        # 該当するcmd_codeのコマンド情報を探す
        command_is_found = False
        for command in response["data"]:
            if int(command["code"], base=16) == cmd_code:
                command_is_found = True
                break

        if not command_is_found:
            raise Exception('Command name "{}" cannot be found.'.format(cmd_code))

        # とりあえずcodeだけ入れてparamは大変なので後で入れる
        command_to_send = {"code": command["code"], "params": []}

        # paramは型情報が必要なので、読み込んだコマンド情報から生成
        for i in range(len(command["params"])):
            command_to_send["params"].append(
                {
                    "type": command["params"][i]["type"],
                    "value": str(cmd_params_value[i]),
                }
            )

        self._send_cmd(command_to_send)
        return

    def _send_cmd(self, command: dict) -> None:
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
        ).json()

        if response["ack"] == False:
            raise Exception(
                'An error has occured while sending command "{}"'.format(command)
            )
