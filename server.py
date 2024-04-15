import os
import io
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pytube import YouTube

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# Read OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Make sure to set OPENAI_API_KEY in your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def download_audio_stream(video_url):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
        audio_buffer = io.BytesIO()
        audio_stream.stream_to_buffer(buffer=audio_buffer)
        audio_buffer.seek(0)  # Reset buffer pointer to the beginning
        audio_buffer.name = "audio.mp4"
        

        return audio_buffer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def transcribe_audio(audio_stream, debug=True):
    try:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream,
        )
        transcript = response.text.strip()
        if debug == True:
            with open('transcript.txt', 'w') as file:
                file.write(transcript)
            with open('response.json', 'w') as file:
                file.write(response.json())
        return transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcript/")
async def get_transcript(video_url: str):
    audio_stream = download_audio_stream(video_url)
    return {"transcript": transcribe_audio(audio_stream)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)