import os
from io import BytesIO
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from opticka_analiza_izvestaja import analyse_document, analyse_audio
from vizualna_anliza_ostecenja import AnalyzeBatchRequest, batch_inspect
from transcriptions_store import TRANSCRIPTION_DATA
from typing import Optional, Literal
import logging
import uuid
import threading

# --- Logging setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)



app = FastAPI(
    title="Vehicle Damage Analyzer",
    description="Analyze vehicle damage images via Google Gemini AI and transcribe audio files using Whisper.",
    version=os.getenv("VERSION"),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.get("/")
def read_root():
    return {"Naslov": "Damage Control API"}


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

    if not req:
        logger.warning("No file uploaded.")
        raise HTTPException(status_code=400, detail="No file provided")

    if not req.image_urls:
        logger.warning("No image URLs provided.")
        raise HTTPException(status_code=400, detail="`image_urls` list required")

    try:
        result = batch_inspect(
            image_urls=req.image_urls,
        )
        logger.info("Batch inspection completed successfully.")
    except Exception as e:
        logger.error(f"Error during batch inspection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


    return {
        "result": result
    }



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
    if not file:
        logger.warning("No file uploaded.")
        raise HTTPException(status_code=400, detail="No file provided")

    if not file.content_type.startswith("audio/"):
        logger.warning("Invalid file type: %s", file.content_type)
        raise HTTPException(status_code=400, detail="Please upload a valid audio file.")

    guid = str(uuid.uuid4())
    TRANSCRIPTION_DATA[guid] = None

    try:
        contents = await file.read()
        file_stream = BytesIO(contents)

        thread = threading.Thread(target=analyse_audio, args=(file_stream, guid))
        thread.start()

        return {"guid": guid}

    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")

@app.get("/get_transcription")
async def get_transcription(guid: str):
    if guid not in TRANSCRIPTION_DATA:
        return {"output": "Transcription doesn't exist"}

    result = TRANSCRIPTION_DATA[guid]
    if result is None:
        return {"output": "Transcription is not yet ready"}

    # Optional: remove to free memory
    del TRANSCRIPTION_DATA[guid]
    return {"output": result}


@app.post("/analyze_report",
        summary = "Analyze a traffic accident report by performing OCR and extracting relevant information",
        description = "Upload an image file (JPG, JPEG, PNG) or a pdf file to receive relevant information.",
        response_description = "Relevant information"
)
async def analyze_report(
        file: UploadFile = File(...),
        document_type: Optional[Literal["general", "eu_report"]] = Form(
            None,
            description="Type of document: must be 'general' or 'eu_report'"
        )
    ):

    if not file:
        logger.warning("No file uploaded.")
        raise HTTPException(status_code=400, detail="No file provided")

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        input_type = "pdf"
    elif filename.endswith((".png", ".jpg", ".jpeg", '.webp')):
        input_type = "image"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Supported file types: PDF, JPEG, PNG.")

    # Read file content
    contents = await file.read()
    file_stream = BytesIO(contents)

    try:
        result = analyse_document(input=file_stream,
                                  input_type=input_type,
                                  document_type=document_type)
        logger.info("Document analysis completed successfully.")

        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Error during report analysis: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)