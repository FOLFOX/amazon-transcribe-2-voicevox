# amazon-transcribe-2-voicevox

Throws voice input to Amazon Transcribe and the returned text to [VOICEVOX](https://voicevox.hiroshiba.jp/) to play the synthesized voice.

## Features
 
- Command line based
- Change Input and output devices
- Change the speaker of VOICEVOX
 
## Requirement
 
- AWS account and its credentials
- Python 3.8.3
- [VOICEVOX](https://voicevox.hiroshiba.jp/) 0.8.2
 
## Usage
### Preparation

1. Set the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to access Amazon Transcribe.

### Start
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

1. Start VOICEVOX.
2. Start with `python run.py`
3. Speak something.
 
## Installation
```
$ git clone https://github.com/FOLFOX/amazon-transcribe-2-voicevox
$ cd amazon-transcribe-2-voicevox
$ pip install -r requirements.txt
```

## Author
[@hydroxyquinol](https://twitter.com/hydroxyquinol)

## License
[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
