#!/usr/bin/env python
# coding: utf-8

# In[1]:

import asyncio
# This example uses the sounddevice library to get an audio stream from the
# microphone. It's not a dependency of the project but can be installed with
# `pip install sounddevice`.
import queue

import sounddevice

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

import json
import requests

from scipy.io.wavfile import read
import io

import argparse

import boto3
import wave
import MeCab

import datetime as dt

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-i", "--input-device", type=int, help="input device ID")
parser.add_argument("-o", "--output-device", type=int, help="output device ID")
parser.add_argument("-c", "--channels", type=int, default=1, help="number of channels")
parser.add_argument("-sp", "--speaker", type=int, default=0, help="Speaker")
parser.add_argument("-syn", "--synthesizer", type=int, default=0, help="Synthesizer")
parser.add_argument("-chk", "--chunk", type=int, default=0, help="chunk")
parser.add_argument("-b", "--blocksize", type=int, default=2, help="blocksize")


args = parser.parse_args()

# In[2]:
isp = True
output_queue = queue.Queue()

# In[3]:

# In[4]:
sounddevice.default.device = [args.input_device, args.output_device]
print(sounddevice.query_devices())

if args.chunk == 0:
    texts_waka = ''
elif args.chunk < 100:
    texts_waka = []
else:
    texts_waka = {}

start_time = dt.datetime.now()
"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""
class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        global texts_waka
        def chanking(texts_waka):
            if args.chunk == 0:
                chank = texts_waka
                texts_waka=''
            elif args.chunk < 100:
                genchank = args.chunk
                if len(texts_waka) > genchank:
                    chank = ''.join(texts_waka[:genchank])
                    texts_waka = texts_waka[genchank:]
                else:
                    if ''.join(texts_waka[-3:]) == '、、、':
                        chank = ''.join(texts_waka)
                        texts_waka = []
                    else:
                        chank = ''
                        texts_waka.append('、')
            else:
                pass
            return chank, texts_waka
        def play_s(r):
            global isp
            isp = False
            print(r[1])
            sounddevice.play(r[0][0],r[0][1],blocking=True)
            isp = True
        def s_or_l(text, texts_waka,ti):
            if args.chunk == 0:
                texts_waka += text
            elif args.chunk < 100:
                t = MeCab.Tagger ('-Owakati -d ../mecab-ipadic-neologd')
                chars = t.parse(text).split(" ")
                texts_waka.extend(chars[:-1])
            else:
                texts_waka[ti] = text

        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        if len(results) > 0:
            if not results[0].is_partial:
                ti = results[0].start_time
                print(start_time+dt.timedelta(seconds=ti))
                text = results[0].alternatives[0].transcript
                s_or_l(text, texts_waka, ti)
        if len(texts_waka) > 0:
            chanking_ = chanking(texts_waka)
            chank = chanking_[0]
            texts_waka = chanking_[1]
            if len(chank) > 0:
                if args.synthesizer == 0:
                    r = await generate_wav_vb(chank, speaker=args.speaker)
                elif args.synthesizer == 1:
                    r = await generate_wav(chank, speaker=args.speaker)
                output_queue.put_nowait([r,chank])
        if not output_queue.empty():
            if args.chunk <= 100:
                if isp:
                    asyncio.get_event_loop().run_in_executor(None, play_s,
                                                             output_queue.get_nowait())
            else:
                pass

async def mic_stream():
    # This function wraps the raw input stream from the microphone forwarding
    # the blocks to an asyncio.Queue.
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    # Be sure to use the correct parameters for the audio stream that matches
    # the audio formats described for the source language you'll be using:
    # https://docs.aws.amazon.com/transcribe/latest/dg/streaming.html
    stream = sounddevice.RawInputStream(
        channels=args.channels,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * args.blocksize,
        dtype="int16",
    )
    # Initiate the audio stream and asynchronously yield the audio chunks
    # as they become available.
    with stream:
        while True:
            indata, status = await input_queue.get()
            yield indata, status

async def write_chunks(stream):
    # This connects the raw audio chunks generator coming from the microphone
    # and passes them along to the transcription stream.
    async for chunk, status in mic_stream():
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()


async def basic_transcribe():
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region="us-west-2")

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="ja-JP",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(stream), handler.handle_events())

async def generate_wav(text, speaker):
    talkers = {0:'Mizuki',1:'Takumi'}
    #Initializing variables
    CHANNELS = 1 #Polly's output is a mono audio stream
    RATE = 16000 #Polly supports 16000Hz and 8000Hz output for PCM format
    FRAMES = []
    WAV_SAMPLE_WIDTH_BYTES = 2 # Polly's output is a stream of 16-bits (2 bytes) samples

    #Initializing Polly Client
    polly = boto3.client("polly")

    #Input text for conversion
    INPUT = '<speak>'
    INPUT += text
    INPUT += '</speak>'
    try:
        response = polly.synthesize_speech(Text=INPUT, TextType="ssml",
                                           OutputFormat="pcm",VoiceId=talkers[speaker],
                                           SampleRate="16000")
    except (BotoCoreError, ClientError) as error:
        sys.exit(-1)

    #Processing the response to audio stream
    STREAM = response.get("AudioStream")
    FRAMES.append(STREAM.read())

    bi_io = io.BytesIO()

    WAVEFORMAT = wave.open(bi_io,'wb')
    WAVEFORMAT.setnchannels(CHANNELS)
    WAVEFORMAT.setsampwidth(WAV_SAMPLE_WIDTH_BYTES)
    WAVEFORMAT.setframerate(RATE)
    WAVEFORMAT.writeframes(b''.join(FRAMES))
    WAVEFORMAT.close()

    bi_io.seek(0)
    rate, data = read(bi_io)
    return [data,rate]

async def generate_wav_vb(text, speaker=0):
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    headers = {'Content-Type': 'application/json',}
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1.json())
    )
    rate, data = read(io.BytesIO(response2.content))
    return [data,rate]
loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()

# In[ ]:




