from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from io import BytesIO
from opticka_analiza_izvestaja import analyse_document
app = FastAPI()

@app.get("/")
def read_root():
    return {"Naslov": "Damage Control API"}


@app.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        input_type = "pdf"
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        input_type = "image"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Read file content
    contents = await file.read()
    file_stream = BytesIO(contents)

    # Call your analysis function
    result = analyse_document(input=file_stream,
                              input_type=input_type)

    return JSONResponse(content=result)


# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
