#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from .operation import Operation


def generate_and_receive_tlm(
    ope: Operation, cmd_code_generate_tlm: int, tlm_code: int
) -> dict:

    _, received_time_prev = ope.get_latest_tlm(tlm_code)

    ope.send_cmd(cmd_code_generate_tlm, (0x40, tlm_code, 1))

    for _ in range(5):
        tlm, received_time_after = ope.get_latest_tlm(tlm_code)
        if received_time_prev != received_time_after:
            return tlm

        time.sleep(1)

    raise Exception("No response to GENERATE_TLM.")


def send_cmd(ope: Operation, cmd_code: int, cmd_args: tuple) -> None:
    ope.send_cmd(cmd_code, cmd_args)
    time.sleep(1)
