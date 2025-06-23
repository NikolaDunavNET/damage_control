import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

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