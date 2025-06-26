from PIL import Image
from io import BytesIO
from konfiguracija import get_document_intel_object, get_openai_credentials
import json
import ast

OUTPUT_FILE_MAPPING = {
    'general': 'generalna_forma_izlaza.json',
    'eu_report': 'eu_izvestaj_forma_izlaze.json'
}

def get_output_form(document_type):
    """
    Get the output form from the document type
    """
    # if document_type is not specified
    if document_type is None:
        document_type = 'general'

    # chose the file path from the dictionary
    if document_type not in OUTPUT_FILE_MAPPING.keys():
        raise ValueError(f"{document_type} is an invalid document type. Please choose 'general' or 'eu_report'.")

    # Load and pass the file
    with open(OUTPUT_FILE_MAPPING[document_type], 'rb') as f:
        output_form = json.load(f)
    return output_form

def extract_info_from_image(file_input,
                            max_size=1000):
    """
    Extract information from an image using Azure Document Intelligence
    Resize image if needed.
    """
    client = get_document_intel_object()
    img = Image.open(file_input)

    # Resize image if needed
    w, h = img.size
    if max(w, h) > max_size:
        factor = max_size / max(w, h)
        img = img.resize((int(w * factor), int(h * factor)), Image.LANCZOS)
    stream = BytesIO()
    img.save(stream, format="PNG")
    stream.seek(0)
    poller = client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=stream,
        content_type="image/png"
    )
    return poller.result()

def extract_info_from_pdf(file_input):
    """
    Extracts information from a PDF file using Azure Document Intelligence
    """
    client = get_document_intel_object()
    poller = client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=file_input,
        content_type="application/pdf"
    )
    return poller.result()

def process_raw_output(ocr_json: str,
                       document_type: str = 'general') -> str:
    """
    Feeds the raw OCR JSON (ocr_json) into the model with a strict system prompt,
    and returns the assistant’s raw text response (your flat JSON).
    """

    model, client = get_openai_credentials()
    format_izlaza = get_output_form(document_type)

    system_prompt = (
        "You are a highly accurate data-extraction tool. "
        "Given the full OCR output from a document, "
        "return ONLY a single, valid JSON object by filling in the values"
        "You will likely be given a text in English or Serbian"
        "Correct some obvious mistakes if esitmate that they are made"
        "but do not write anything else"
        f"here is the format of the output: {format_izlaza}"
    )

    user_prompt = f"**INPUT**\n{ocr_json}"

    messages = [
        {"role": "system",  "content": system_prompt},
        {"role": "user",    "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
    )

    raw = response.choices[0].message.content.strip()

    # Strip Markdown formatting if present
    clean_response = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        # Fallback: try parsing as Python dict if it uses single quotes
        try:
            return ast.literal_eval(clean_response)
        except Exception as fallback_error:
            # Final fallback: raise an error with useful info
            raise ValueError(
                f"Failed to parse LLM output.\nRaw output:\n{raw}\n\nJSON error: {e}\nLiteral eval error: {fallback_error}")

def analyse_document(input,
                     input_type='image',
                     document_type='general'):
    """
    Performs document analysis and returns the output
    """
    if input_type == 'image':
        document_intelligence_output = extract_info_from_image(input)
    elif input_type == 'pdf':
        document_intelligence_output = extract_info_from_pdf(input)
    else:
        raise ValueError("Invalid input type. Please choose 'image' or 'pdf'.")

    processed_output = process_raw_output(document_intelligence_output.content,
                                          document_type=document_type)

    return processed_output


if __name__ == "__main__":
    with open('generalna_forma_izlaza.json', 'rb') as f:
        general_report = json.load(f)
    print(general_report)


