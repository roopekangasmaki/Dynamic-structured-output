from google import genai
from google.genai import types
from pydantic import create_model
from typing import Optional
from datetime import date, time, datetime

def prepare_schema_model(schema_json):
    """
    Convert a schema to a Pydantic model.
    This function prepares the schema for structured output.
    To use this function, the schema should be in JSON format,
    and it should contain at least fields "Field" and "Type".
    """
    if isinstance(schema_json, str):
        schema_data = json.loads(schema_json)
    else:
        schema_data = schema_json
    
    field_definitions = {}
    for field_def in schema_data:
        field_name = field_def["Field"]
        field_type = field_def["Type"]
        
        # Map the field type to Python types
        type_mapping = {
            "string": str,
            "float": float,
            "int": int,
            "date": date,
            "time": time,
            "datetime": datetime,
            "boolean": bool
        }
        
        python_type = type_mapping.get(field_type, str)
        # Make all fields optional with None as default
        field_definitions[field_name] = (Optional[python_type], None)
    
    # Create a dynamic Pydantic model
    ExtractedData = create_model("ExtractedData", **field_definitions)
    return ExtractedData


def create_extraction_instructions(schema_data, format_style="default"):
    """
    Create extraction instructions from schema data i.e. prompt.
    """
    # Build the basic field descriptions
    fields_text = "\n".join([
        f"- {field['Field']}: {field['Type']}" + 
        (f" ({field['Description']})" if field.get('Description') else "")
        for field in schema_data
    ])
    
    instructions = {
        "fields_list": fields_text,
        "field_names": [field["Field"] for field in schema_data],
        "field_types": {field["Field"]: field["Type"] for field in schema_data},
        "field_descriptions": {
            field["Field"]: field.get("Description", "") 
            for field in schema_data
        }
    }
    
    # Default formatted prompt text
    if format_style == "default" or format_style == "google":
        print("Using default format style")
        instructions["prompt_text"] = f"""
        Extract the following information from the document:
        {fields_text}
        
        Return ONLY the extracted data in a JSON format with these exact field names.
        If a field cannot be found in the document, return null for that field.
        """
    return instructions


def extract_with_gemini(file_content, instructions, pydantic_model, api_key, model="gemini-2.0-flash"):
    """Extract data using Google Gemini Document Understanding."""
    # Initialize the Gemini API client
    client = genai.Client(api_key=api_key)
    
    # Generate structured output using Document Understanding
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(
                data=file_content, 
                mime_type="application/pdf"
                ),
                instructions["prompt_text"]
        ],
        config={
            'response_mime_type': 'application/json',
            'response_schema': pydantic_model,
        }
    )
    
    # Return the structured data
    return json.loads(response.text)


def extract(file_content, schema_json, api_key, provider="google"):
    """Extract structured data from the given file content based on the schema."""
    # Parse schema data
    schema_data = json.loads(schema_json) if isinstance(schema_json, str) else schema_json
    
    # Convert schema to Pydantic model (provider-agnostic)
    pydantic_model = prepare_schema_model(schema_data)
    
    # Create extraction instructions based on provider
    instructions = create_extraction_instructions(
        schema_data, 
        format_style=provider
    )
    
    return extract_with_gemini(file_content, instructions, pydantic_model, api_key)
