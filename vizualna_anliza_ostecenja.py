from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
import json
import urllib.request
from google.genai import types
from konfiguracija import VEHICLE_PARTS_CONFIGURATION, get_gemini_credentials

GEMINI_CLIENT, GEMINI_MODEL_NAME = get_gemini_credentials()

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

    CONFIG = {VEHICLE_PARTS_CONFIGURATION}

    Here are the images you will receive, in order:
    {image_list_text}

    Now return ONLY this single JSON object, with exactly these keys:
    {{
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

    resp = GEMINI_CLIENT.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=parts
    )
    return parse_gemini_output(resp.text)


class AnalyzeBatchRequest(BaseModel):
    image_urls: List[str] = Field(
        ...,
        description="List of image URLs to analyze for vehicle damage",
        example=[
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg",
        ],
    )