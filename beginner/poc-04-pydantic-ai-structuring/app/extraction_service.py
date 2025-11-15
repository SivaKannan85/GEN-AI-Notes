"""
Service for extracting structured data using OpenAI function calling.
"""
import logging
import json
from typing import Type, TypeVar, Any, Dict
from pydantic import BaseModel
from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ExtractionService:
    """Service for extracting structured data from text using OpenAI."""

    def __init__(self):
        """Initialize extraction service."""
        self.settings = get_settings()
        self.client = OpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.openai_timeout
        )

    def _pydantic_to_function_schema(self, model: Type[BaseModel]) -> Dict:
        """
        Convert Pydantic model to OpenAI function schema.

        Args:
            model: Pydantic model class

        Returns:
            Function schema dictionary
        """
        schema = model.model_json_schema()

        # Build function parameters from schema
        parameters = {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }

        # Remove definitions if present (not needed in function schema)
        if "$defs" in schema:
            # Inline definitions into properties
            self._inline_definitions(parameters["properties"], schema["$defs"])

        return parameters

    def _inline_definitions(self, properties: Dict, definitions: Dict):
        """Inline schema definitions into properties."""
        for key, value in properties.items():
            if isinstance(value, dict):
                # Handle $ref references
                if "$ref" in value:
                    ref_path = value["$ref"].split("/")[-1]
                    if ref_path in definitions:
                        properties[key] = definitions[ref_path]
                # Handle arrays with $ref
                elif "items" in value and isinstance(value["items"], dict) and "$ref" in value["items"]:
                    ref_path = value["items"]["$ref"].split("/")[-1]
                    if ref_path in definitions:
                        value["items"] = definitions[ref_path]
                # Recursively process nested objects
                elif "properties" in value:
                    self._inline_definitions(value["properties"], definitions)

    def extract_structured_data(
        self,
        text: str,
        model: Type[T],
        function_name: str,
        function_description: str,
        system_prompt: str = None
    ) -> T:
        """
        Extract structured data from text using OpenAI function calling.

        Args:
            text: Input text to extract from
            model: Pydantic model class to extract into
            function_name: Name of the function for OpenAI
            function_description: Description of what the function does
            system_prompt: Optional system prompt

        Returns:
            Instance of the Pydantic model with extracted data

        Raises:
            ValueError: If extraction fails or model validation fails
        """
        logger.info(f"Extracting structured data using model: {model.__name__}")

        # Build function schema from Pydantic model
        parameters = self._pydantic_to_function_schema(model)

        # Define the function
        functions = [
            {
                "name": function_name,
                "description": function_description,
                "parameters": parameters
            }
        ]

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": text})

        try:
            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                functions=functions,
                function_call={"name": function_name},  # Force function call
                temperature=self.settings.temperature
            )

            # Extract function call arguments
            message = response.choices[0].message

            if not message.function_call:
                raise ValueError("No function call in response")

            # Parse arguments
            arguments_str = message.function_call.arguments
            arguments = json.loads(arguments_str)

            # Validate and create Pydantic model instance
            result = model(**arguments)

            logger.info(f"Successfully extracted data into {model.__name__}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from function call: {e}")
            raise ValueError(f"Invalid JSON in function call response: {e}")
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise ValueError(f"Failed to extract structured data: {e}")

    def extract_with_confidence(
        self,
        text: str,
        model: Type[T],
        function_name: str,
        function_description: str,
        system_prompt: str = None
    ) -> tuple[T, float]:
        """
        Extract structured data with confidence score.

        Args:
            text: Input text
            model: Pydantic model class
            function_name: Function name
            function_description: Function description
            system_prompt: Optional system prompt

        Returns:
            Tuple of (extracted_data, confidence_score)
        """
        # Extract data
        data = self.extract_structured_data(
            text=text,
            model=model,
            function_name=function_name,
            function_description=function_description,
            system_prompt=system_prompt
        )

        # Calculate simple confidence based on field completion
        # (In production, you might use logprobs or a separate confidence model)
        total_fields = len(model.model_fields)
        filled_fields = sum(
            1 for field_name in model.model_fields
            if getattr(data, field_name) is not None
            and getattr(data, field_name) != []
            and getattr(data, field_name) != {}
            and getattr(data, field_name) != ""
        )

        confidence = filled_fields / total_fields if total_fields > 0 else 0.0

        return data, confidence


# Global extraction service instance
_extraction_service: ExtractionService = None


def get_extraction_service() -> ExtractionService:
    """Get the global extraction service instance."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
