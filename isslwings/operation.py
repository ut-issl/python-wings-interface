#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from typing import Tuple

import requests

if os.environ.get("USES_DOCKER") != None:
    default_url = "http://host.docker.internal:5000"
else:
    default_url = "http://localhost:5000"


class Operation:
    def __init__(self, operation_idx: int = 0, url: str = default_url):
        self.url = url

        response = requests.get("{}/api/operations".format(self.url)).json()

        if not response["data"]:
            raise Exception("Selected operation does not exist.")

        self.operation_id = response["data"][operation_idx]["id"]

    def get_latest_tlm(self, tlm_code_id: int) -> Tuple[dict, str]:
        response = requests.get(
            "{}/api/operations/{}/tlm".format(self.url, self.operation_id)
        ).json()

        if not response["data"]:
            raise Exception("Telemetries are not stored.")

        # 該当するtlm_code_nameのテレメ情報を探す
        tlm_code_is_found = False
        for response_data in response["data"]:
            if int(response_data["packetInfo"]["id"], base=16) == tlm_code_id:
                tlm_code_is_found = True
                break

        if not tlm_code_is_found:
            raise Exception(
                'Telemetry code id "{}" cannot be found.'.format(tlm_code_id)
            )

        telemetry_data = {}
        telemetries = response_data["telemetries"]

        for telemetry in telemetries:

            # TODO: テレメデータがない時の例外処理を加える

            # strで読み込んでしまっているので、適切な型へcastする
            # int -> float の順で変換に失敗したらstrで読む
            try:
                data = int(telemetry["value"])
            except:
                try:
                    data = float(telemetry["value"])
                except:
                    data = telemetry["value"]

            telemetry_data[telemetry["name"]] = data

        # テレメトリごとに更新時刻は保存されているが、とりあえず先頭を抽出
        received_time = telemetries[0]["time"]

        return telemetry_data, received_time

    def send_cmd(self, cmd_code: int, cmd_params_value: tuple) -> None:
        response = requests.get(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id)
        ).json()

        if not response["data"]:
            raise Exception("An error has occurred while fetching cmd info from WINGS.")

        # 該当するcmd_codeのコマンド情報を探す
        command_is_found = False
        for command in response["data"]:
            if int(command["code"], base=16) == cmd_code:
                command_is_found = True
                break

        if not command_is_found:
            raise Exception('Command code id "{}" cannot be found.'.format(cmd_code))

        # 送信用dictにとりあえずcodeだけ入れて、paramは大変なので後で入れる
        command_to_send = {"code": command["code"], "params": []}

        # paramは型情報が必要なので、最初に読み込んだコマンド情報から生成
        for i in range(len(command["params"])):
            command_to_send["params"].append(
                {
                    "type": command["params"][i]["type"],
                    "value": str(cmd_params_value[i]),
                }
            )

        self._send_cmd(command_to_send)

    def _send_cmd(self, command: dict) -> None:
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
        ).json()

        if response["ack"] == False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))
