#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

import isslwings as wings

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, default="http://localhost:5000", help="")
parser.add_argument("--operation_index", type=int, default=-1, help="")
args = parser.parse_args()

BC_TL_INITIAL = 20
BC_AR_GS_RELATES_PROCESS = 43
Tlm_CODE_BL = 0x0021


def main():
    ope = wings.Operation(operation_idx=args.operation_index, url=args.url)
    ope.send_cmd("Cmd_BCT_SET_BLOCK_POSITION", (BC_TL_INITIAL, 0))
    time.sleep(1)
    ope.send_cmd("Cmd_GENERATE_TLM", (0x40, Tlm_CODE_BL, 1))
    time.sleep(3)

    tlm_BL = ope.get_latest_tlm("BL")
    assert int(tlm_BL["CMD0_ID"]) == ope.get_cmd_id("Cmd_BCT_ROTATE_BLOCK")
    assert int(tlm_BL["CMD0_TI"]) == 0
    assert int(tlm_BL["CMD0_PARAM0"]) == 0
    assert int(tlm_BL["CMD0_PARAM1"]) == BC_AR_GS_RELATES_PROCESS


if __name__ == "__main__":
    main()
