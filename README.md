# amazon-transcribe-2-voicevox
 
音声入力をAmazon Transcribeに投げて返ってきたテキストを、  
[VOICEVOX](https://voicevox.hiroshiba.jp/)に投げて返ってきた音声を再生します。
 
## 機能
 
- コマンドラインベース
- 入力・出力デバイスを変更可能
- VOICEVOXの話者を変更可能
 
## 必要要件
 
- AWSアカウントとその認証情報
- Python 3.8.3
- [VOICEVOX](https://voicevox.hiroshiba.jp/) 0.8.2
 
## 使い方
### 準備

1. Amazon Transcribeにアクセス可能な`AWS_ACCESS_KEY_ID`と`AWS_SECRET_ACCESS_KEY`を環境変数に設定する。

### 起動
```
$ python run.py -h
usage: run.py [-h] [-i INPUT_DEVICE] [-o OUTPUT_DEVICE] [-c CHANNELS] [-sp SPEAKER]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DEVICE, --input-device INPUT_DEVICE
                        input device ID
  -o OUTPUT_DEVICE, --output-device OUTPUT_DEVICE
                        output device ID
  -c CHANNELS, --channels CHANNELS
                        number of channels
  -sp SPEAKER, --speaker SPEAKER
                        VOICEVOX speaker
```

1. VOICEVOXを起動しておく。
2. `python run.py`で起動する。
3. なんか喋る。
 
## インストール
 
```
$ git clone https://github.com/FOLFOX/amazon-transcribe-2-voicevox
$ cd amazon-transcribe-2-voicevox
$ pip install -r requirements.txt
```

## 作者
[@hydroxyquinol](https://twitter.com/hydroxyquinol)
 
## ライセンス
[Apache License, Version 2.0](https://licenses.opensource.jp/Apache-2.0/Apache-2.0.html)
