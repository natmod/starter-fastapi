import os
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pytube import YouTube

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

OUTPUT_PATH = "temp"
# Read OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Make sure to set OPENAI_API_KEY in your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def download_audio_from_youtube(video_url):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp:
            audio_stream.download(output_path=OUTPUT_PATH, filename=temp.name)
            return os.path.join(OUTPUT_PATH, temp.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def transcribe_audio(audio_path, debug=False):
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            transcript = response.text.strip()
            if debug == True:
                with open('temp/transcript.txt', 'w') as file:
                    file.write(transcript)
                with open('temp/response.json', 'w') as file:
                    file.write(response.json())
            return transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcript/")
async def get_transcript(video_url: str):
    audio_path = download_audio_from_youtube(video_url)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return {"transcript": transcribe_audio(audio_path)}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)