import uvicorn
from fastapi import FastAPI, HTTPException, Path, Body, File, UploadFile
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import requests
import json
import urllib.request
import datetime
from google.genai import types
from google import genai
from dotenv import load_dotenv
from faster_whisper import WhisperModel
import tempfile

#load_dotenv()
# --- Configuration & Client setup ------------------------------------------------
#API_KEY = os.getenv("GEMINI_API_KEY")
#print(API_KEY)
GEMINI_API_KEY = "AIzaSyClArbf77SHWFgtDdE7f9pbcZLyb2EugdQ"
MODEL_NAME = "gemini-2.0-flash-exp"  # "gemini-1.5-pro"
client = genai.Client(api_key=GEMINI_API_KEY)

CONFIG = {

    "groups": [
        "Car body",
        "Lighting system",
        "Major Damage",
        "Other",
        "Technical area",
        "Tyres",
        "Windows"
    ],
    "parts": [
        "(Inner) Wheel arch, front",
        "(Inner) Wheel arch, rear",
        "Aluminium rim front",
        "Aluminium rim rear",
        "Beverage holder, rear",
        "Bonnet",
        "Boot / Rear door bottom",
        "Boot / Rear door center",
        "Boot / Rear door handle",
        "Boot / Rear door lock",
        "Boot / Trunk lid lining, inside",
        "Boot / Trunk spoiler",
        "Bumper grill",
        "Bumper loading strip",
        "Bumper protection strip front",
        "Bumper protection strip rear",
        "Bumper, front",
        "Bumper, rear",
        "Cargo space floor, rear",
        "Center side panel, middle",
        "Damage unknown",
        "Dashboard switches",
        "Door handle front, outside",
        "Door handle rear, outside",
        "Door lock",
        "Door trim rear, inside",
        "Door, front",
        "Door, front edge",
        "Door, front inner sill",
        "Door, front moulding strip",
        "Door, rear",
        "Door, rear edge",
        "Door, rear inner sill plate",
        "Door, rear moulding strip",
        "Emblem / Logo",
        "Emblem / Logo  rim, front",
        "Emblem / Logo, rim, rear",
        "Fender (US)",
        "Fog light",
        "Footmat, rear",
        "Front damage",
        "Fuel tank flap",
        "Grill",
        "Headlight",
        "Hood (US)",
        "Indicator - outside mirror",
        "Indicator, rear",
        "License plate",
        "Lift-/Tailgate (US)",
        "Luggage space cover",
        "Parking sensor, rear",
        "Quarter window, rear",
        "Quarterpanel (US)",
        "Radio Antenna",
        "Reflector, rear",
        "Rocker panel (US)",
        "Roof center",
        "Roof front",
        "Roof pillar (A), front",
        "Roof rails",
        "Roof rear",
        "Seat, 2nd row (rear seat)",
        "Seat, front",
        "Side damage, driver side",
        "Side panel, rear, bottom",
        "Side panel, rear, centre",
        "Side panel, rear, top",
        "Side view Mirror",
        "Side window, front",
        "Sill, front",
        "Sill, rear",
        "Sliding door, center",
        "Spare wheel",
        "Spoiler, bumper, front",
        "Steel rim front",
        "Steel rim rear",
        "Tailgate",
        "Taillight",
        "Tire front",
        "Tire rear",
        "Total loss",
        "Tow eye cover",
        "Underbody damage",
        "Vehicle does not start",
        "Wheel arch, front",
        "Wheel arch, rear",
        "Wheel cover front",
        "Wheel cover rear",
        "Windscreen",
        "Windshield (US)",
        "Wing / Fender, front",
        "Wing / Fender, rear",
        "Wiper arm, rear",
        "Wiper blade, rear"
    ],
    "types": [
        "Crack",
        "Dent",
        "Graffiti",
        "Not needed",
        "Stone chip with crack",
        "broken",
        "crash",
        "defective",
        "dented",
        "dirt",
        "hail damage",
        "hole",
        "leaky",
        "loose",
        "missing",
        "scratch",
        "stone chip",
        "superficial damage (UK)"
    ],
    "sides": [
        "Driver side",
        "Not needed",
        "Passenger side",
        "front",
        "middle",
        "rear"
    ],
    "severities": [
        "5-10 cm (down to primer)",
        "5-10 cm superficial",
        "< 5 cm (down to primer)",
        "< 5 cm superficial",
        "> 10 cm (down to primer)",
        "> 10 cm (with paint damage)",
        "> 10 cm (without paint damage)",
        "> 10 cm superficial",
        "> 3 cm (with paint damage)",
        "> 3 cm (without paint damage)",
        "Not needed",
        "complete",
        "driver's vision",
        "glass only",
        "not in driver's vision",
        "not in driver's vision < 2cm w/o crack",
        "surface only",
        "surrounding",
        "up to 1 cm (with paint damage)",
        "up to 1 cm (without paint damage)",
        "up to 3 cm (with paint damage)",
        "up to 3cm (without paint damage)"
    ],
    "projections": [
        "BACK_SIDE",
        "DRIVER_SIDE",
        "FRONT_SIDE",
        "PASSENGER_SIDE",
        "TOP",
        "UNKNOWN_PROJECTION"
    ],
    "segments": [
        "BOTTOM_LEFT",
        "BOTTOM_MID",
        "BOTTOM_RIGHT",
        "MID_LEFT",
        "MID_MID",
        "MID_RIGHT",
        "TOP_LEFT",
        "TOP_MID",
        "TOP_RIGHT"
    ]

}



# --- Util functions

def get_case_images2(
    damage_case_id: str = "",
    auth_token: str = "",
    source: str = "AAA-1-RENT",
    key: str = "damageCaseId"
) -> List[str]:
    api = (
        "https://api-prod.orange.sixt.com/v1/vehicle-damage/"
        f"external/damage-cases?key={key}&value={damage_case_id}&source={source}"
    )
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(api, headers=headers)
    res = response.json()

    image_urls: List[str] = []
    if isinstance(res, list):
        for case in res:
            for damage in case.get("damages", []):
                for coord in damage.get("coordinates", []):
                    for photo in coord.get("photos", []):
                        url = photo.get("url")
                        if url:
                            image_urls.append(url)
    return image_urls


def parse_gemini_output(raw_text: str) -> Dict[str, Any]:
    try:
        json_text = raw_text.strip()
        # strip markdown fences if present
        for fence in ("```json", "```"):
            if json_text.startswith(fence):
                json_text = json_text.split(fence, 1)[1]
        if json_text.endswith("```"):
            json_text = json_text.rsplit("```", 1)[0]
        return json.loads(json_text)
    except Exception as e:
        print(f"Error parsing Gemini output: {e}")
        return {"error": str(e), "raw_text": raw_text}


def batch_inspect(
    image_urls: List[str],
    MODEL: str,
    CONFIG: Dict[str, Any],
    client: genai.Client
) -> Dict[str, Any]:
    parts: List[types.Part] = []

    for url in image_urls:
        try:
            resp = urllib.request.urlopen(url)
            blob = resp.read()
            parts.append(types.Part.from_bytes(data=blob, mime_type="image/jpeg"))
        except Exception as e:
            print(f"Error downloading image {url}: {e}")

    image_list_text = "\n".join(f"{i+1}) {url.split('/')[-1]}" for i, url in enumerate(image_urls))

    prompt = f"""System: You are an expert car-damage inspector.

    CONFIG = {CONFIG}

    Here are the images you will receive, in order:
    {image_list_text}

    Now return ONLY this single JSON object, with exactly these keys:
    {{
      "damageCaseId":  "...",
      "caseNumber":    "...",
      "createdAt":     "...",
      "damages": [
        {{
          "group":     "<one of CONFIG[\\"groups\\"]>",
          "part":      "<one of CONFIG[\\"parts\\"]>",
          "type":      "<one of CONFIG[\\"types\\"]>",
          "side":      "<one of CONFIG[\\"sides\\"]>",
          "severity":  "<one of CONFIG[\\"severities\\"]>",
          "coordinates": [
            {{
              "projection": "<one of CONFIG[\\"projections\\"]>",
              "segment":    "<one of CONFIG[\\"segments\\"]>",
              "photos": [
                {{ "type":"OVERVIEW_WITH_REGISTRATION","photoId":"","url":"","preDamagePhoto":false }},
                {{ "type":"DAMAGE_AREA",               "photoId":"","url":"","preDamagePhoto":false }},
                {{ "type":"DAMAGE_DETAIL",             "photoId":"","url":"","preDamagePhoto":false }}
              ]
            }}
          ]
        }}
        /* one per unique damage index … */
      ]
    }}
    Do NOT output any extra text or markdown—only the raw JSON."""

    parts.append(types.Part.from_text(text=prompt))

    resp = client.models.generate_content(
        model=MODEL,
        contents=parts
    )
    return parse_gemini_output(resp.text)



app = FastAPI(
    title="Vehicle Damage Analyzer",
    description="Analyze vehicle damage images via Google Gemini AI and transcribe audio files using Whisper.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


class AnalyzeBatchRequest(BaseModel):
    image_urls: List[str] = Field(
        ...,
        description="List of image URLs to analyze for vehicle damage",
        example=[
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg"
        ]
    )


@app.post(
    "/analyze_batch",
    summary="Batch-inspect damage images",
    description="Submit a JSON body containing a list of image URLs and receive structured vehicle damage data.",
    response_description="Structured damage data and metadata"
)
async def analyze_batch(req: AnalyzeBatchRequest):
    """
    Batch-inspect a set of vehicle damage images.
    - **image_urls**: required list of URLs pointing to damage images.
    - **case_id**, **case_number**, **created_at**: optional fields echoed back.
    """
    if not req.image_urls:
        raise HTTPException(status_code=400, detail="`image_urls` list required")

    try:
        result = batch_inspect(
            image_urls=req.image_urls,
            MODEL=MODEL_NAME,
            CONFIG=CONFIG,
            client=client
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    return {
        "result": result,
        "metadata": {
            "image_count": len(req.image_urls),
            "timestamp": datetime.datetime.now().isoformat()
        }
    }


model = WhisperModel("large-v3-turbo")


@app.post(
    "/transcribe",
    summary="Transcribe an audio file",
    description="Upload an audio file (MP3, WAV, etc.) and receive a text transcription.",
    response_description="Transcript of the uploaded audio"
)
async def transcribe_audio(
    file: UploadFile = File(
        ...,
        description="The audio file to transcribe (supported formats: MP3, WAV, etc.)"
    )
):
    """
    Transcribe an uploaded audio file into text.
    - **file**: audio file to be transcribed.
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Please upload a valid audio file.")

    data = await file.read()
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(data)
    tmp.close()  # MUST close on Windows
    try:
        segments, _ = model.transcribe(tmp.name)
    finally:
        os.unlink(tmp.name)

    transcript = "".join(s.text for s in segments)
    return {"transcript": transcript}

if __name__ == "__main__":
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8080, reload=True)