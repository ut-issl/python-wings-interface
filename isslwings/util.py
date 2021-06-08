#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from .operation import Operation


def generate_and_receive_tlm(
    ope: Operation, cmd_code_generate_tlm: int, tlm_code: int
) -> dict:

    _, received_time_prev = ope.get_latest_tlm(tlm_code)

    ope.send_rt_cmd(cmd_code_generate_tlm, (0x40, tlm_code, 1))

    for _ in range(5):
        time.sleep(1)

        tlm, received_time_after = ope.get_latest_tlm(tlm_code)
        if received_time_prev != received_time_after:
            return tlm

    raise Exception("No response to GENERATE_TLM.")


def send_rt_cmd_and_confirm(
    ope: Operation, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
) -> None:
    # HKが見える前提で組む

    func_send_cmd = lambda cmd_code, cmd_args: ope.send_rt_cmd(cmd_code, cmd_args)
    return _send_cmd_and_confirm(ope, func_send_cmd, cmd_code, cmd_args, tlm_code_hk)


def send_bl_cmd_and_confirm(
    ope: Operation, ti: int, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
) -> None:
    # HKが見える前提で組む

    func_send_cmd = lambda cmd_code, cmd_args: ope.send_bl_cmd(ti, cmd_code, cmd_args)
    return _send_cmd_and_confirm(ope, func_send_cmd, cmd_code, cmd_args, tlm_code_hk)


def _send_cmd_and_confirm(
    ope, func_send_cmd, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
):
    tlm_HK, _ = ope.get_latest_tlm(tlm_code_hk)
    command_count_before = tlm_HK["HK.OBC_GS_CMD_COUNTER"]

    func_send_cmd(cmd_code, cmd_args)

    for _ in range(5):
        time.sleep(1)

        tlm_HK, _ = ope.get_latest_tlm(tlm_code_hk)
        command_count_after = tlm_HK["HK.OBC_GS_CMD_COUNTER"]
        command_exec_id = tlm_HK["HK.OBC_GS_CMD_LAST_EXEC_ID"]

        if command_count_after > command_count_before and command_exec_id == cmd_code:
            return tlm_HK["HK.OBC_GS_CMD_LAST_EXEC_STS"]

    raise Exception("No response to command code:" + str(cmd_code) + ".")


def send_cmd(ope: Operation, cmd_code: int, cmd_args: tuple) -> None:
    """
    !! Deprecated !!

    Please use "send_rt_cmd_and_confirm" insted.
    """

    ope.send_rt_cmd(cmd_code, cmd_args)
    time.sleep(1)


def send_cmd_and_confirm(
    ope: Operation, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
) -> None:
    """
    !! Deprecated !!

    Please use "send_rt_cmd_and_confirm" insted.
    """

    func_send_cmd = lambda cmd_code, cmd_args: ope.send_rt_cmd(cmd_code, cmd_args)
    return _send_cmd_and_confirm(ope, func_send_cmd, cmd_code, cmd_args, tlm_code_hk)
