"""
Unit tests for the Pydantic AI Structuring application.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models import (
    ContactInfo,
    Recipe,
    Ingredient,
    EventInfo,
    ProductInfo,
    SentimentAnalysis,
    SentimentType,
    ProductCategory
)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_contact_extraction():
    """Mock contact extraction response."""
    return (
        ContactInfo(
            name="John Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            company="Acme Corp",
            address="123 Main St"
        ),
        0.95
    )


@pytest.fixture
def mock_recipe_extraction():
    """Mock recipe extraction response."""
    return (
        Recipe(
            title="Chocolate Chip Cookies",
            description="Classic cookies",
            ingredients=[
                Ingredient(name="flour", quantity="2 cups", preparation="sifted"),
                Ingredient(name="sugar", quantity="1 cup")
            ],
            instructions=["Preheat oven", "Mix ingredients", "Bake"],
            prep_time="15 minutes",
            cook_time="10 minutes",
            servings="24 cookies"
        ),
        0.92
    )


@pytest.fixture
def mock_event_extraction():
    """Mock event extraction response."""
    return (
        EventInfo(
            title="Team Meeting",
            description="Quarterly planning",
            date="2024-01-15",
            time="2:00 PM",
            location="Conference Room A",
            organizer="Jane Smith",
            attendees=["John Doe", "Alice Johnson"]
        ),
        0.88
    )


@pytest.fixture
def mock_product_extraction():
    """Mock product extraction response."""
    return (
        ProductInfo(
            name="Wireless Headphones",
            category=ProductCategory.ELECTRONICS,
            price="$99.99",
            brand="AudioTech",
            description="High-quality wireless headphones",
            features=["Bluetooth 5.0", "30-hour battery"],
            specifications={"weight": "250g"}
        ),
        0.90
    )


@pytest.fixture
def mock_sentiment_extraction():
    """Mock sentiment extraction response."""
    return (
        SentimentAnalysis(
            sentiment=SentimentType.POSITIVE,
            confidence=0.92,
            positive_aspects=["Great quality", "Fast shipping"],
            negative_aspects=["Expensive"],
            summary="Overall positive with minor price concerns"
        ),
        0.92
    )


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch('app.extraction_service.ExtractionService.extract_with_confidence')
def test_extract_contact_info_success(mock_extract, client, mock_contact_extraction):
    """Test successful contact information extraction."""
    # Setup mock
    mock_extract.return_value = mock_contact_extraction

    # Make request
    request_data = {
        "text": "Contact John Doe at john.doe@example.com or call (555) 123-4567. He works at Acme Corp, 123 Main St."
    }
    response = client.post("/extract/contact", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    assert len(data["contacts"]) == 1
    assert data["contacts"][0]["name"] == "John Doe"
    assert data["contacts"][0]["email"] == "john.doe@example.com"
    assert data["confidence"] == 0.95


def test_extract_contact_invalid_request(client):
    """Test contact extraction with invalid request."""
    response = client.post("/extract/contact", json={"text": ""})
    assert response.status_code == 422  # Validation error


@patch('app.extraction_service.ExtractionService.extract_with_confidence')
def test_extract_recipe_success(mock_extract, client, mock_recipe_extraction):
    """Test successful recipe extraction."""
    # Setup mock
    mock_extract.return_value = mock_recipe_extraction

    # Make request
    request_data = {
        "text": "Chocolate Chip Cookies: Mix 2 cups flour with 1 cup sugar. Preheat oven, then bake."
    }
    response = client.post("/extract/recipe", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "recipe" in data
    assert data["recipe"]["title"] == "Chocolate Chip Cookies"
    assert len(data["recipe"]["ingredients"]) == 2
    assert len(data["recipe"]["instructions"]) == 3
    assert data["confidence"] == 0.92


@patch('app.extraction_service.ExtractionService.extract_with_confidence')
def test_extract_event_info_success(mock_extract, client, mock_event_extraction):
    """Test successful event extraction."""
    # Setup mock
    mock_extract.return_value = mock_event_extraction

    # Make request
    request_data = {
        "text": "Team Meeting on 2024-01-15 at 2:00 PM in Conference Room A, organized by Jane Smith"
    }
    response = client.post("/extract/event", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "events" in data
    assert len(data["events"]) == 1
    assert data["events"][0]["title"] == "Team Meeting"
    assert data["events"][0]["date"] == "2024-01-15"
    assert data["confidence"] == 0.88


@patch('app.extraction_service.ExtractionService.extract_with_confidence')
def test_extract_product_info_success(mock_extract, client, mock_product_extraction):
    """Test successful product extraction."""
    # Setup mock
    mock_extract.return_value = mock_product_extraction

    # Make request
    request_data = {
        "text": "Wireless Headphones by AudioTech for $99.99. High-quality with Bluetooth 5.0 and 30-hour battery."
    }
    response = client.post("/extract/product", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 1
    assert data["products"][0]["name"] == "Wireless Headphones"
    assert data["products"][0]["price"] == "$99.99"
    assert data["products"][0]["brand"] == "AudioTech"
    assert data["confidence"] == 0.90


@patch('app.extraction_service.ExtractionService.extract_with_confidence')
def test_extract_sentiment_success(mock_extract, client, mock_sentiment_extraction):
    """Test successful sentiment analysis."""
    # Setup mock
    mock_extract.return_value = mock_sentiment_extraction

    # Make request
    request_data = {
        "text": "Great quality product with fast shipping, but a bit expensive."
    }
    response = client.post("/extract/sentiment", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert data["analysis"]["sentiment"] == "positive"
    assert data["analysis"]["confidence"] == 0.92
    assert "Great quality" in data["analysis"]["positive_aspects"]


@patch('app.extraction_service.ExtractionService.extract_with_confidence')
def test_extraction_error_handling(mock_extract, client):
    """Test error handling when extraction fails."""
    # Setup mock to raise error
    mock_extract.side_effect = ValueError("Extraction failed")

    # Make request
    request_data = {"text": "Some text"}
    response = client.post("/extract/contact", json=request_data)

    # Should return 400 for ValueError
    assert response.status_code == 400


def test_all_extraction_endpoints_exist(client):
    """Test that all extraction endpoints are accessible."""
    endpoints = [
        "/extract/contact",
        "/extract/recipe",
        "/extract/event",
        "/extract/product",
        "/extract/sentiment"
    ]

    for endpoint in endpoints:
        # Check endpoint exists (will fail validation, but endpoint should exist)
        response = client.post(endpoint, json={"text": ""})
        assert response.status_code in [200, 400, 422]  # Not 404
