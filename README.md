# python-wings-interface

## 概要
localhostで立ち上げたWINGSでのC2A動作試験をpythonで行うためにライブラリ。

## インストール方法
特に細かいことを気にしないのであれば開発者モードでインストールする

```
git clone https://gitlab.com/ut_issl/users/kanta_yangida/python-wings-interface
cd python-wings-interface
pip install -e .
```

## サンプルコード
Initial modeのブロックコマンドを確認
```
import isslwings as wings

BC_TL_INITIAL = 20
Cmd_CODE_BCT_ROTATE_BLOCK = 16
BC_AR_GS_RELATES_PROCESS = 43

operation_id = wings.get_operation_id(0)

wings.send_set_block_pos(operation_id, str(BC_TL_INITIAL), "0")
time.sleep(1)
wings.send_generate_tlm(operation_id, "0x0021")
time.sleep(1)
bl = wings.get_latest_tlm(operation_id, "BL")

assert bl[11]["value"] == str(Cmd_CODE_BCT_ROTATE_BLOCK)
assert bl[12]["value"] == str(0)
assert bl[13]["value"] == str(0)
assert bl[14]["value"] == str(BC_AR_GS_RELATES_PROCESS)
```
