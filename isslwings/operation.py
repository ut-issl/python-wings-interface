#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from typing import Tuple

import requests

if os.environ.get("USES_DOCKER") != None:
    default_url = "http://host.docker.internal:5000"
else:
    default_url = "http://localhost:5000"


class Operation:
    def __init__(self, operation_idx: int = 0, url: str = default_url) -> None:
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

        time.sleep(0.1)

        return telemetry_data, received_time

    def send_rt_cmd(self, cmd_code: int, cmd_params_value: tuple) -> None:
        command_to_send = self._generate_cmd_dict(cmd_code, cmd_params_value)
        self._send_rt_cmd(command_to_send)

        time.sleep(0.1)

    def send_bl_cmd(self, ti: int, cmd_code: int, cmd_params_value: tuple) -> None:
        command_to_send = self._generate_cmd_dict(cmd_code, cmd_params_value)
        self._send_bl_cmd(ti, command_to_send)

        time.sleep(0.1)

    def _generate_cmd_dict(self, cmd_code: int, cmd_params_value: tuple) -> dict:
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

        return command_to_send

    def _send_rt_cmd(self, command: dict) -> None:

        command["ExecType"] = "RT"
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
        ).json()

        if response["ack"] == False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))

    def _send_bl_cmd(self, ti: int, command: dict) -> None:

        command["execType"] = "BL"
        command["execTime"] = ti
        response = requests.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
        ).json()

        if response["ack"] == False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))
