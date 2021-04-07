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

    wings.util.send_cmd(
        ope, c2a_enum.Cmd_CODE_BCT_SET_BLOCK_POSITION, (c2a_enum.BC_TL_INITIAL, 0)
    )

    tlm_BL = wings.util.generate_and_receive_tlm(
        ope, c2a_enum.Cmd_CODE_GENERATE_TLM, c2a_enum.Tlm_CODE_BL
    )

    assert tlm_BL["CMD0_ID"] == c2a_enum.Cmd_CODE_BCT_ROTATE_BLOCK
    assert tlm_BL["CMD0_TI"] == 0
    assert tlm_BL["CMD0_PARAM0"] == 0
    assert tlm_BL["CMD0_PARAM1"] == c2a_enum.BC_AR_GS_RELATED_PROCESS


if __name__ == "__main__":
    test_initial_tl()
