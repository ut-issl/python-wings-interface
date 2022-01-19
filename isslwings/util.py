#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from typing import Callable
from .operation import Operation


def generate_and_receive_tlm(
    ope: Operation, cmd_code_generate_tlm: int, tlm_code: int
) -> dict:

    _, received_time_prev = ope.get_latest_tlm(tlm_code)

    ope.send_rt_cmd(cmd_code_generate_tlm, (0x40, tlm_code, 1))

    for _ in range(50):
        time.sleep(0.2)

        tlm, received_time_after = ope.get_latest_tlm(tlm_code)
        if received_time_prev != received_time_after:
            return tlm

    raise Exception("No response to GENERATE_TLM.")


# FIXME: MOBC経由からの2nd OBCへのコマンドは，GS counterで confirm できないので，一旦対応しない．別関数つくる？
def send_rt_cmd_and_confirm(
    ope: Operation, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
) -> str:
    # HKが見える前提で組む

    func_send_cmd: Callable[
        [int, tuple], None
    ] = lambda cmd_code, cmd_args: ope.send_rt_cmd(cmd_code, cmd_args)
    return _send_cmd_and_confirm(ope, func_send_cmd, cmd_code, cmd_args, tlm_code_hk)


# FIXME: MOBC経由からの2nd OBCへのコマンドは，GS counterで confirm できないので，一旦対応しない．別関数つくる？
def send_bl_cmd_and_confirm(
    ope: Operation, ti: int, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
) -> str:
    # HKが見える前提で組む

    func_send_cmd: Callable[
        [int, tuple], None
    ] = lambda cmd_code, cmd_args: ope.send_bl_cmd(ti, cmd_code, cmd_args)
    return _send_cmd_and_confirm(ope, func_send_cmd, cmd_code, cmd_args, tlm_code_hk)


# TODO: HK で confirm する過程を追加する
def send_tl_cmd(
    ope: Operation, ti: int, cmd_code: int, cmd_args: tuple
) -> str:
    ope.send_tl_cmd(ti, cmd_code, cmd_args)


# TODO: HK で confirm する過程を追加する
def send_utl_cmd(
    ope: Operation, unixtime: float, cmd_code: int, cmd_args: tuple
) -> str:
    ope.send_utl_cmd(unixtime, cmd_code, cmd_args)


def _send_cmd_and_confirm(
    ope: Operation,
    func_send_cmd: Callable[[int, tuple], None],
    cmd_code: int,
    cmd_args: tuple,
    tlm_code_hk: int,
) -> str:
    hk_tlm_info = ope.get_obc_info()["hk_tlm_info"]
    hk_tlm_name = hk_tlm_info["tlm_name"]
    tlm_HK, _ = ope.get_latest_tlm(tlm_code_hk)
    command_count_before = tlm_HK[hk_tlm_name + "." + hk_tlm_info["cmd_counter"]]

    func_send_cmd(cmd_code, cmd_args)

    for _ in range(50):
        time.sleep(0.2)

        tlm_HK, _ = ope.get_latest_tlm(tlm_code_hk)
        command_count_after = tlm_HK[hk_tlm_name + "." + hk_tlm_info["cmd_counter"]]
        command_exec_id = tlm_HK[hk_tlm_name + "." + hk_tlm_info["cmd_last_exec_id"]]

        if command_count_after > command_count_before and command_exec_id == cmd_code:
            return tlm_HK[hk_tlm_name + "." + hk_tlm_info["cmd_last_exec_sts"]]

    raise Exception("No response to command code:" + str(cmd_code) + ".")


def send_cmd(ope: Operation, cmd_code: int, cmd_args: tuple) -> None:
    """
    !! Deprecated !!

    Please use "send_rt_cmd_and_confirm" instead.
    """

    ope.send_rt_cmd(cmd_code, cmd_args)
    time.sleep(1)


def send_cmd_and_confirm(
    ope: Operation, cmd_code: int, cmd_args: tuple, tlm_code_hk: int
) -> str:
    """
    !! Deprecated !!

    Please use "send_rt_cmd_and_confirm" instead.
    """

    func_send_cmd = lambda cmd_code, cmd_args: ope.send_rt_cmd(cmd_code, cmd_args)
    return _send_cmd_and_confirm(ope, func_send_cmd, cmd_code, cmd_args, tlm_code_hk)
