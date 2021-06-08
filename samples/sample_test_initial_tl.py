#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import time

import c2aenum as c2a
import isslwings as wings

with open(os.path.dirname(__file__).replace("\\", "/") + "/settings.json") as f:
    json_dict = json.load(f)
c2a_abs_path = os.path.dirname(__file__).replace("\\", "/") + json_dict["c2a_rel_path"]
c2a_enum = c2a.load_enum(c2a_abs_path)


ope = wings.Operation()


def test_initial_tl():

    ret = wings.util.send_rt_cmd_and_confirm(
        ope,
        c2a_enum.Cmd_CODE_BCT_SET_BLOCK_POSITION,
        (c2a_enum.BC_TL_INITIAL, 0),
        c2a_enum.Tlm_CODE_HK,
    )
    assert ret == "SUC:G"

    tlm_BL = wings.util.generate_and_receive_tlm(
        ope, c2a_enum.Cmd_CODE_GENERATE_TLM, c2a_enum.Tlm_CODE_BL
    )
    assert tlm_BL["BL.CMD0_ID"] == c2a_enum.Cmd_CODE_BCT_ROTATE_BLOCK
    assert tlm_BL["BL.CMD0_TI"] == 0
    assert tlm_BL["BL.CMD0_PARAM0"] == 0
    assert tlm_BL["BL.CMD0_PARAM1"] == c2a_enum.BC_AR_GS_RELATED_PROCESS


def test_add_bc():

    ret = wings.util.send_rt_cmd_and_confirm(
        ope,
        c2a_enum.Cmd_CODE_BCT_SET_BLOCK_POSITION,
        (300, 0),
        c2a_enum.Tlm_CODE_HK,
    )
    assert ret == "SUC:G"
    tlm_HK = wings.util.generate_and_receive_tlm(
        ope, c2a_enum.Cmd_CODE_GENERATE_TLM, c2a_enum.Tlm_CODE_HK
    )
    assert tlm_HK["HK.OBC_BCT_BLK_PTR"] == 300
    assert tlm_HK["HK.OBC_BCT_CMD_PTR"] == 0

    ret = wings.util.send_bl_cmd_and_confirm(
        ope,
        1,
        c2a_enum.Cmd_CODE_GENERATE_TLM,
        (0x40, c2a_enum.Tlm_CODE_HK, 1),
        c2a_enum.Tlm_CODE_HK,
    )
    tlm_HK = wings.util.generate_and_receive_tlm(
        ope, c2a_enum.Cmd_CODE_GENERATE_TLM, c2a_enum.Tlm_CODE_HK
    )
    assert tlm_HK["HK.OBC_BCT_BLK_PTR"] == 300
    assert tlm_HK["HK.OBC_BCT_CMD_PTR"] == 1
    assert tlm_HK["HK.OBC_BCT_REGD_TIME"] == 1
    assert tlm_HK["HK.OBC_BCT_REGD_ID"] == c2a_enum.Cmd_CODE_GENERATE_TLM


if __name__ == "__main__":
    test_initial_tl()
    test_add_bc()
