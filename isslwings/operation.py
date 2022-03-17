#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import os
import time
from typing import Tuple
import httpx

if os.environ.get("USES_DOCKER") is not None:
    default_url = "http://host.docker.internal:5000"
else:
    default_url = "https://localhost:5001"

default_obc_info = {
    "name": "MOBC",
    "hk_tlm_info": {
        "tlm_name": "HK",
        "cmd_counter": "OBC_GS_CMD_COUNTER",
        "cmd_last_exec_id": "OBC_GS_CMD_LAST_EXEC_ID",
        "cmd_last_exec_sts": "OBC_GS_CMD_LAST_EXEC_STS",
    },
}

default_authentication_info = {
    "client_id": "hoge_id",
    "client_secret": "hoge_secret",
    "grant_type": "hoge",
    "username": "hoge@fuga",
    "password": "piyopiyo",
}


class Operation:
    def __init__(
        self,
        url: str = default_url,
        auto_connect: bool = True,
        obc_info: dict = default_obc_info,
        authentication_info: dict = default_authentication_info,
    ) -> None:
        self.url = url
        self.operation_id = ""
        self.obc_info = obc_info
        self.authorized_headers = {}  # 認証が必要

        # 認証を入れていく
        self.client = httpx.Client(http2=True, verify=False)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        contents = ""
        for key in authentication_info.keys():
            contents += f"{key}={authentication_info[key]}&"
        response_with_token = self.client.post(
            f"{self.url}/connect/token", headers=headers, content=contents.rstrip("&")
        )
        access_token = json.loads(response_with_token.text)["access_token"]

        self.authorized_headers = dict(Authorization=f"Bearer {access_token}")

        if auto_connect is True:
            self.connect_to_operation_by_idx(0)

    def connect_to_operation_by_path_number(self, path_number: str) -> None:
        response = self.client.get(
            "{}/api/operations".format(self.url), headers=self.authorized_headers
        ).json()
        if not response["data"]:
            raise Exception("Selected operation does not exist.")

        found = False
        for operation_info in response["data"]:
            if operation_info["pathNumber"] == path_number:
                self.operation_id = operation_info["id"]
                found = True
                break
        if not found:
            raise Exception('Path number "' + path_number + '" was not found.')

    def connect_to_operation_by_idx(self, operation_idx: int) -> None:
        response = self.client.get(
            "{}/api/operations".format(self.url), headers=self.authorized_headers
        ).json()

        if not response["data"]:
            raise Exception("Selected operation does not exist.")

        self.operation_id = response["data"][operation_idx]["id"]

    def connect_to_operation_by_id(self, operation_id: str) -> None:
        self.operation_id = operation_id

    def delete_all_operations(self) -> None:
        response = self.client.get(
            "{}/api/operations".format(self.url), headers=self.authorized_headers
        ).json()
        if not response["data"]:
            # operation dows not exist
            return

        for operation_info in response["data"]:
            response = self.client.delete(
                "{}/api/operations/{}".format(self.url, operation_info["id"]),
                headers=self.authorized_headers,
            )

            if response.status_code != 204:
                raise Exception("Failed to delete operation")

    def start_and_connect_to_new_operation(self, component_name: str):

        # まずはコンポーネント名からIDへの対応を取りに行く
        response = self.client.get(
            "{}/api/components".format(self.url), headers=self.authorized_headers
        ).json()
        if not response["data"]:
            raise Exception("An error occurred while fetching components' data.")

        component_id = ""
        for component_info in response["data"]:
            if component_info["name"] == component_name:
                component_id = component_info["id"]
                break
        if component_id == "":
            raise Exception('Component "' + component_name + '" was not found.')

        # コンポーネントIDが判明したので、パスを作る
        now = datetime.datetime.now()
        path_number = "{:02d}{:02d}{:02d}-{:02d}{:02d}".format(
            now.year % 100, now.month, now.day, now.hour, now.minute
        )

        headers = self.authorized_headers
        headers["Content-Type"] = "application/json"

        response = self.client.post(
            "{}/api/operations".format(self.url),
            json={
                "operation": {
                    "pathNumber": path_number,
                    "comment": "",
                    "fileLocation": "Local",
                    "tmtcTarget": "TmtcIf",
                    "componentId": component_id,
                    "satelliteId": "",
                    "planId": "",
                }
            },
            headers=headers,
        )
        if response.status_code != 201:
            raise Exception("Failed to start operation.")

        self.connect_to_operation_by_path_number(path_number)

    def get_latest_tlm(self, tlm_code_id: int) -> Tuple[dict, str]:
        response = self.client.get(
            "{}/api/operations/{}/tlm".format(self.url, self.operation_id),
            headers=self.authorized_headers,
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
            raise Exception('Telemetry code id "{}" cannot be found.'.format(tlm_code_id))

        telemetry_data = {}
        telemetries = response_data["telemetries"]

        for telemetry in telemetries:

            # TODO: テレメデータがない時の例外処理を加える

            # strで読み込んでしまっているので、適切な型へcastする
            # hexはそのまま
            # その他は int -> float の順で変換に失敗したらstrで読む
            if telemetry["telemetryInfo"]["convType"] == "HEX":
                data = telemetry["telemetryValue"]["value"]
            else:
                try:
                    data = int(telemetry["telemetryValue"]["value"])
                except (ValueError, TypeError):
                    try:
                        data = int(telemetry["telemetryValue"]["value"], base=16)
                    except (ValueError, TypeError):
                        try:
                            data = float(telemetry["telemetryValue"]["value"])
                        except (ValueError, TypeError):
                            data = telemetry["telemetryValue"]["value"]

            telemetry_data[telemetry["telemetryInfo"]["name"]] = data

        # テレメトリごとに更新時刻は保存されているが、とりあえず先頭を抽出
        received_time = telemetries[0]["telemetryValue"]["time"]

        time.sleep(0.2)

        return telemetry_data, received_time

    def send_rt_cmd(self, cmd_code: int, cmd_params_value: tuple, component: str = "") -> None:
        command_to_send = self._generate_cmd_dict(cmd_code, cmd_params_value, component)
        self._send_rt_cmd(command_to_send)

        time.sleep(0.1)

    def send_bl_cmd(
        self, ti: int, cmd_code: int, cmd_params_value: tuple, component: str = ""
    ) -> None:
        command_to_send = self._generate_cmd_dict(cmd_code, cmd_params_value, component)
        self._send_bl_cmd(ti, command_to_send)

        time.sleep(0.1)

    def send_tl_cmd(
        self, ti: int, cmd_code: int, cmd_params_value: tuple, component: str = ""
    ) -> None:
        command_to_send = self._generate_cmd_dict(cmd_code, cmd_params_value, component)
        self._send_tl_cmd(ti, command_to_send)

        time.sleep(0.1)

    def send_utl_cmd(
        self, unixtime: float, cmd_code: int, cmd_params_value: tuple, component: str = ""
    ) -> None:
        command_to_send = self._generate_cmd_dict(cmd_code, cmd_params_value, component)
        self._send_utl_cmd(unixtime, command_to_send)

        time.sleep(0.1)

    def get_obc_info(self) -> dict:
        return self.obc_info

    def _generate_cmd_dict(
        self, cmd_code: int, cmd_params_value: tuple, component: str = ""
    ) -> dict:
        if component == "":
            component = self.obc_info["name"]

        response = self.client.get(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            headers=self.authorized_headers,
        ).json()

        if not response["data"]:
            raise Exception("An error has occurred while fetching cmd info from WINGS.")

        # 該当するcmd_codeのコマンド情報を探す
        command_is_found = False
        for command in response["data"]:
            if command["component"] == component and int(command["code"], base=16) == cmd_code:
                command_is_found = True
                break

        if not command_is_found:
            raise Exception('Command code id "{}" cannot be found.'.format(cmd_code))

        # 送信用dictにとりあえずtemplateを入れる
        command_to_send = command

        # paramは型情報が必要なので、最初に読み込んだコマンド情報から生成
        for i in range(len(command["params"])):
            command_to_send["params"][i] = {
                "type": command["params"][i]["type"],
                "value": str(cmd_params_value[i]),
            }

        return command_to_send

    def _send_rt_cmd(self, command: dict) -> None:
        command["execType"] = "RT"
        response = self.client.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
            headers=self.authorized_headers,
        ).json()

        if response["ack"] is False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))

    def _send_bl_cmd(self, ti: int, command: dict) -> None:
        command["execType"] = "BL"
        command["execTime"] = ti
        response = self.client.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
            headers=self.authorized_headers,
        ).json()

        if response["ack"] is False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))

    def _send_tl_cmd(self, ti: int, command: dict) -> None:
        command["execType"] = "TL"
        command["execTime"] = ti
        response = self.client.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
            headers=self.authorized_headers,
        ).json()

        if response["ack"] is False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))

    def _send_utl_cmd(self, unixtime: float, command: dict) -> None:
        command["execType"] = "UTL"
        command["execTime"] = unixtime
        response = self.client.post(
            "{}/api/operations/{}/cmd".format(self.url, self.operation_id),
            json={"command": command},
            headers=self.authorized_headers,
        ).json()

        if response["ack"] is False:
            raise Exception('send_cmd failed.\n" + "command "{}"'.format(command))


if __name__ == "__main__":
    ope = Operation(auto_connect=False)
    ope.delete_all_operations()
    ope.start_and_connect_to_new_operation("MOBC")
