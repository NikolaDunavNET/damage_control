from io import BytesIO
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
import datetime
from opticka_analiza_izvestaja import analyse_document, process_raw_output
from vizualna_anliza_ostecenja import AnalyzeBatchRequest, batch_inspect
from typing import Optional
from faster_whisper import WhisperModel
import logging

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


WHISPER_MODEL_NAME = "large-v3-turbo"

# FastAPI app
app = FastAPI(
    title="Vehicle Damage Analyzer",
    description="Analyze vehicle damage images via Google Gemini AI and transcribe audio files using Whisper.",
    version="1.1.2",
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

model = WhisperModel(WHISPER_MODEL_NAME)

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
        logger.warning("Invalid file type: %s", file.content_type)
        raise HTTPException(status_code=400, detail="Please upload a valid audio file.")

    try:
        contents = await file.read()
        file_stream = BytesIO(contents)

        # Produce transcript
        segments, _ = model.transcribe(file_stream)
        logger.info(f"Transcription completed successfully.")
        transcript = "".join(s.text for s in segments)

        # extract information from transcript
        extracted_output = process_raw_output(transcript)

        extracted_output['transcript'] = transcript

        return extracted_output
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
@app.post("/analyze_report",
        summary = "Analyze a traffic accident report by performing OCR and extracting relevant information",
        description = "Upload an image file (JPG, JPEG, PNG) or a pdf file to receive relevant information.",
        response_description = "Relevant information"
)
async def analyze_report(
        file: UploadFile = File(...),
        document_type: Optional[str] = Form(None)

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