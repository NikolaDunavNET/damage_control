import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from google.genai import types
from google import genai

load_dotenv()

def get_document_intel_object():
    """
    Loads necessary environment variables and returns a DocumentIntelligenceClient object
    """
    API_KEY = os.getenv("DNET_API_KEY")
    endpoint = os.getenv("DNET_ENDPOINT")
    credentials = AzureKeyCredential(API_KEY)

    document_intelligence_client = DocumentIntelligenceClient(endpoint, credentials)

    return document_intelligence_client

def get_openai_credentials():
    client = AzureOpenAI(
        api_version= os.environ["API_VERSION"],
        azure_endpoint=os.environ["DNET_AZURE_ENDPOINT"],
        api_key=os.environ["DNET_OPENAI_API_KEY"],
    )
    model = "gpt-4o"

    return model, client

def get_gemini_credentials():
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
    client = genai.Client(api_key=GEMINI_API_KEY)

    return client, MODEL_NAME

VEHICLE_PARTS_CONFIGURATION = {

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