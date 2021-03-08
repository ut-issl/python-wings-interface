#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

import isslwings as wings

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, default="http://localhost:5000", help="")
args = parser.parse_args()

BC_TL_INITIAL = 20
Cmd_CODE_BCT_ROTATE_BLOCK = 16
BC_AR_GS_RELATES_PROCESS = 43
Tlm_CODE_BL = 0x21


def main():
    ope = wings.Operation(operation_idx=0, url=args.url)
    ope.send_set_block_pos(BC_TL_INITIAL, 0)
    time.sleep(1)
    ope.send_generate_tlm(Tlm_CODE_BL)
    time.sleep(3)
    bl = ope.get_latest_tlm("BL")

    assert int(bl["CMD0_ID"]) == Cmd_CODE_BCT_ROTATE_BLOCK
    assert int(bl["CMD0_TI"]) == 0
    assert int(bl["CMD0_PARAM0"]) == 0
    assert int(bl["CMD0_PARAM1"]) == BC_AR_GS_RELATES_PROCESS


if __name__ == "__main__":
    main()
