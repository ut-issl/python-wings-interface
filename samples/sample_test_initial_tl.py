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


def test_initial_tl():
    ope = wings.Operation()
    ope.send_cmd(c2a_enum.Cmd_CODE_BCT_SET_BLOCK_POSITION, (c2a_enum.BC_TL_INITIAL, 0))
    time.sleep(1)
    ope.send_cmd(c2a_enum.Cmd_CODE_GENERATE_TLM, (0x40, c2a_enum.Tlm_CODE_BL, 1))
    time.sleep(2)

    tlm_BL = ope.get_latest_tlm("BL")
    assert tlm_BL["CMD0_ID"] == c2a_enum.Cmd_CODE_BCT_ROTATE_BLOCK
    assert tlm_BL["CMD0_TI"] == 0
    assert tlm_BL["CMD0_PARAM0"] == 0
    assert tlm_BL["CMD0_PARAM1"] == c2a_enum.BC_AR_GS_RELATED_PROCESS


if __name__ == "__main__":
    test_initial_tl()
