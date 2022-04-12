# python-wings-interface

## 概要
localhostで立ち上げたWINGSでのC2A動作試験をpythonで行うためにライブラリ。

## インストール方法

特に細かいことを気にしないのであれば開発者モードでインストールする。

インストールしなくてもこのライブラリは使用できるがpytestは実行できず、各testファイルを直接実行する必要がある。

```
git clone https://github.com/ut-issl/python-wings-interface.git
cd python-wings-interface
pip install -e .
```

## 使い方

以下、`python-wings-interface/` を基準のパスとして考える。

### サンプルコード
`samples/sample_test_*.py` を参照。

これらのtestを走らせたい場合は `run_sample.bat` を実行する。

### テスト作成方法
`samples/sample_test_*.py` から参考にするファイルを `./` に `test_*.py` という名前でコピーし、編集する。

`test_*` という名称の関数を作り、必要なパラメータに対して `assert` を実行する。

### テスト実行方法

準備として以下を行っておく。
1. wingsを立ち上げてoperationを開始する、もしくはすでに開始されていることを確認する。
2. wings-tmtc-ifからそのoperationへ接続を行う。（この時、最も新しいoperationを使用すること。）
3. S2Eを立ち上げてテレメトリがwings-tmtc-ifに到達していることを確認する。

この状態で以下を実行すると `./test_*.py` 内の `test_*` という名称の関数のテストが全て実行される。

```
pytest
```
