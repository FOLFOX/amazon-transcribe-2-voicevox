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

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-i", "--input-device", type=int, help="input device ID")
parser.add_argument("-o", "--output-device", type=int, help="output device ID")
parser.add_argument("-c", "--channels", type=int, default=1, help="number of channels")
parser.add_argument("-sp", "--speaker", type=int, default=0, help="VOICEVOX speaker")

args = parser.parse_args()

# In[2]:
isp = True
output_queue = queue.Queue()

# In[3]:

# In[4]:
sounddevice.default.device = [args.input_device, args.output_device]
print(sounddevice.query_devices())

"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""
class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        def play_s(r):
            global isp
            rate, data = read(io.BytesIO(r[0]))
            isp = False
            print(r[1])
            sounddevice.play(data,rate,blocking=True)
            isp = True
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        if len(results) > 0:
            if not results[0].is_partial:
                text = results[0].alternatives[0].transcript
                r = await generate_wav_np(text, speaker=args.speaker)
                output_queue.put_nowait([r,text])
        if not output_queue.empty():
            if isp:
                asyncio.get_event_loop().run_in_executor(None, play_s,
                                                         output_queue.get_nowait())

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
        blocksize=1024 * 2,
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

async def generate_wav_np(text, speaker=0):
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
    return response2.content

loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()

# In[ ]:




