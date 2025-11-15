"""
Pydantic models for structured AI outputs.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum


# Request/Response models for API

class ExtractionRequest(BaseModel):
    """Base request for extraction."""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to extract information from")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Contact John Doe at john.doe@example.com or call (555) 123-4567"
            }
        }


# Structured output models for different extraction types

class ContactInfo(BaseModel):
    """Contact information extracted from text."""
    name: Optional[str] = Field(None, description="Person's full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")
    address: Optional[str] = Field(None, description="Physical address")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "(555) 123-4567",
                "company": "Acme Corp",
                "address": "123 Main St, City, State 12345"
            }
        }


class ContactExtractionResponse(BaseModel):
    """Response for contact extraction."""
    contacts: List[ContactInfo] = Field(..., description="List of extracted contacts")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of extraction")


class Ingredient(BaseModel):
    """Recipe ingredient."""
    name: str = Field(..., description="Ingredient name")
    quantity: Optional[str] = Field(None, description="Quantity (e.g., '2 cups', '1 tablespoon')")
    preparation: Optional[str] = Field(None, description="Preparation note (e.g., 'diced', 'melted')")


class Recipe(BaseModel):
    """Recipe extracted from text."""
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Recipe description")
    ingredients: List[Ingredient] = Field(default_factory=list, description="List of ingredients")
    instructions: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    prep_time: Optional[str] = Field(None, description="Preparation time")
    cook_time: Optional[str] = Field(None, description="Cooking time")
    servings: Optional[str] = Field(None, description="Number of servings")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Chocolate Chip Cookies",
                "description": "Classic homemade cookies",
                "ingredients": [
                    {"name": "flour", "quantity": "2 cups", "preparation": "sifted"},
                    {"name": "butter", "quantity": "1 cup", "preparation": "softened"}
                ],
                "instructions": ["Preheat oven to 350°F", "Mix ingredients", "Bake for 10 minutes"],
                "prep_time": "15 minutes",
                "cook_time": "10 minutes",
                "servings": "24 cookies"
            }
        }


class RecipeExtractionResponse(BaseModel):
    """Response for recipe extraction."""
    recipe: Recipe = Field(..., description="Extracted recipe")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class EventInfo(BaseModel):
    """Event information extracted from text."""
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    date: Optional[str] = Field(None, description="Event date")
    time: Optional[str] = Field(None, description="Event time")
    location: Optional[str] = Field(None, description="Event location")
    organizer: Optional[str] = Field(None, description="Event organizer")
    attendees: Optional[List[str]] = Field(default_factory=list, description="List of attendees")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Team Meeting",
                "description": "Quarterly planning session",
                "date": "2024-01-15",
                "time": "2:00 PM - 3:30 PM",
                "location": "Conference Room A",
                "organizer": "Jane Smith",
                "attendees": ["John Doe", "Alice Johnson"]
            }
        }


class EventExtractionResponse(BaseModel):
    """Response for event extraction."""
    events: List[EventInfo] = Field(..., description="List of extracted events")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ProductCategory(str, Enum):
    """Product categories."""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    BOOKS = "books"
    HOME = "home"
    TOYS = "toys"
    SPORTS = "sports"
    OTHER = "other"


class ProductInfo(BaseModel):
    """Product information extracted from text."""
    name: str = Field(..., description="Product name")
    category: Optional[ProductCategory] = Field(None, description="Product category")
    price: Optional[str] = Field(None, description="Product price")
    brand: Optional[str] = Field(None, description="Brand name")
    description: Optional[str] = Field(None, description="Product description")
    features: Optional[List[str]] = Field(default_factory=list, description="Key features")
    specifications: Optional[dict] = Field(default_factory=dict, description="Technical specifications")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Headphones",
                "category": "electronics",
                "price": "$99.99",
                "brand": "AudioTech",
                "description": "High-quality wireless headphones with noise cancellation",
                "features": ["Bluetooth 5.0", "30-hour battery", "Active noise cancellation"],
                "specifications": {"weight": "250g", "battery": "2000mAh"}
            }
        }


class ProductExtractionResponse(BaseModel):
    """Response for product extraction."""
    products: List[ProductInfo] = Field(..., description="List of extracted products")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class SentimentType(str, Enum):
    """Sentiment types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""
    sentiment: SentimentType = Field(..., description="Overall sentiment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    positive_aspects: Optional[List[str]] = Field(default_factory=list, description="Positive aspects mentioned")
    negative_aspects: Optional[List[str]] = Field(default_factory=list, description="Negative aspects mentioned")
    summary: Optional[str] = Field(None, description="Brief summary of sentiment")

    class Config:
        json_schema_extra = {
            "example": {
                "sentiment": "positive",
                "confidence": 0.92,
                "positive_aspects": ["Great quality", "Fast shipping"],
                "negative_aspects": ["Expensive"],
                "summary": "Overall positive review with minor price concerns"
            }
        }


class SentimentExtractionResponse(BaseModel):
    """Response for sentiment analysis."""
    analysis: SentimentAnalysis = Field(..., description="Sentiment analysis result")


class KeyValuePair(BaseModel):
    """Key-value pair for generic extraction."""
    key: str = Field(..., description="Key name")
    value: str = Field(..., description="Value")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence for this pair")


class GenericExtractionResponse(BaseModel):
    """Response for generic key-value extraction."""
    data: List[KeyValuePair] = Field(..., description="Extracted key-value pairs")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")


# Health and error responses

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Extraction failed",
                "detail": "Unable to parse the provided text"
            }
        }
