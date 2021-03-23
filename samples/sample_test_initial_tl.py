#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

import isslwings as wings

BC_TL_INITIAL = 20
BC_AR_GS_RELATES_PROCESS = 43
Tlm_CODE_BL = 0x0021


def test_initial_tl():
    ope = wings.Operation()
    ope.send_cmd("Cmd_BCT_SET_BLOCK_POSITION", (BC_TL_INITIAL, 0))
    time.sleep(1)
    ope.send_cmd("Cmd_GENERATE_TLM", (0x40, Tlm_CODE_BL, 1))
    time.sleep(2)

    tlm_BL = ope.get_latest_tlm("BL")
    assert int(tlm_BL["CMD0_ID"]) == ope.get_cmd_id("Cmd_BCT_ROTATE_BLOCK")
    assert int(tlm_BL["CMD0_TI"]) == 0
    assert int(tlm_BL["CMD0_PARAM0"]) == 0
    assert int(tlm_BL["CMD0_PARAM1"]) == BC_AR_GS_RELATES_PROCESS
