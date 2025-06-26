from io import BytesIO
from vizualna_anliza_ostecenja import batch_inspect
from fastapi import FastAPI, HTTPException, Path, Body, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import datetime
from opticka_analiza_izvestaja import analyse_document
#from vizualna_anliza_ostecenja import AnalyzeBatchRequest, batch_inspect
from pydantic import BaseModel, Field
from typing import List
from faster_whisper import WhisperModel
import tempfile

app = FastAPI(
    title="Vehicle Damage Analyzer",
    description="Analyze vehicle damage images via Google Gemini AI and transcribe audio files using Whisper.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.get("/")
def read_root():
    return {"Naslov": "Damage Control API"}

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

    contents = await file.read()
    file_stream = BytesIO(contents)

    segments, _ = model.transcribe(file_stream)

    transcript = "".join(s.text for s in segments)
    return {"transcript": transcript}

@app.post("/analyze-report",
        summary = "Analyze a traffic accident report by performing OCR and extracting relevant information",
        description = "Upload an image file (JPG, JPEG, PNG) or a pdf file to receive relevant information.",
        response_description = "Relevant information"
)
async def analyze_report(
        document_type: str = Form(...),
        file: UploadFile = File(...),
    ):



    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        input_type = "pdf"
    elif filename.endswith((".png", ".jpg", ".jpeg")):
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    return JSONResponse(content=result)


# Run the app
"""if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
"""