#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests


def get_operation_id(operation_idx: int) -> str:
    response = requests.get("http://localhost:5000/api/operations").json()
    return response["data"][operation_idx]["id"]
