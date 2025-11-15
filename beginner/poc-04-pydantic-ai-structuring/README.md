# POC 4: Pydantic AI Response Structuring

A production-ready system for extracting structured data from unstructured text using Pydantic models and OpenAI function calling. Demonstrates how to transform free-form text into validated, type-safe Python objects.

## Overview

This POC showcases:
- OpenAI function calling for structured outputs
- Pydantic models for data validation and type safety
- Multiple extraction types (contacts, recipes, events, products, sentiment)
- Automatic schema generation from Pydantic models
- Confidence scoring for extractions
- FastAPI endpoints for different extraction tasks
- Comprehensive error handling and validation
- Unit tests with mocked OpenAI responses

## Tech Stack

- **FastAPI**: Web framework for API endpoints
- **OpenAI**: GPT-3.5-turbo with function calling
- **Pydantic**: Data validation and schema definition
- **Uvicorn**: ASGI server

## Project Structure

```
poc-04-pydantic-ai-structuring/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application and endpoints
│   ├── models.py                # Pydantic models for structured data
│   ├── config.py                # Configuration management
│   └── extraction_service.py    # OpenAI function calling service
├── tests/
│   ├── __init__.py
│   └── test_main.py             # Unit tests
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Features

### 1. OpenAI Function Calling
- **Automatic schema generation**: Convert Pydantic models to OpenAI function schemas
- **Type-safe extractions**: Pydantic validates all extracted data
- **Deterministic outputs**: Temperature=0 for consistent results
- **Error handling**: Graceful handling of extraction failures

### 2. Multiple Extraction Types
- **Contact Information**: Names, emails, phone numbers, companies, addresses
- **Recipes**: Ingredients, instructions, times, servings
- **Events**: Title, date, time, location, organizer, attendees
- **Products**: Name, category, price, brand, features, specifications
- **Sentiment Analysis**: Sentiment type, positive/negative aspects, summary

### 3. Pydantic Models
- **Field validation**: Min/max lengths, regex patterns, type checking
- **Optional fields**: Flexible data extraction
- **Nested models**: Complex data structures (e.g., ingredients in recipes)
- **Enums**: Controlled vocabularies (e.g., sentiment types, product categories)
- **Custom validators**: Additional validation logic

### 4. Confidence Scoring
- **Field completion**: Based on how many fields were successfully extracted
- **Threshold-based filtering**: Configurable confidence thresholds
- **Quality metrics**: Assess extraction reliability

### 5. Production Features
- Environment-based configuration
- Structured logging
- Comprehensive error handling
- Request/response validation
- Unit tests with mocks
- Automatic API documentation

## Setup

### Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Navigate to this POC:**
   ```bash
   cd beginner/poc-04-pydantic-ai-structuring
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

   Example `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo-1106
   TEMPERATURE=0.0
   LOG_LEVEL=INFO
   ```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python -m app.main
```

The API will be available at: `http://localhost:8000`

### API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET** `/health`

Check service status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Extract Contact Information

**POST** `/extract/contact`

Extract contact information from text.

**Request Body:**
```json
{
  "text": "Contact John Doe at john.doe@example.com or call (555) 123-4567. He works at Acme Corp, located at 123 Main St, New York, NY 10001."
}
```

**Response:**
```json
{
  "contacts": [
    {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "(555) 123-4567",
      "company": "Acme Corp",
      "address": "123 Main St, New York, NY 10001"
    }
  ],
  "confidence": 1.0
}
```

### 3. Extract Recipe

**POST** `/extract/recipe`

Extract recipe information from text.

**Request Body:**
```json
{
  "text": "Chocolate Chip Cookies\\n\\nIngredients:\\n- 2 cups flour\\n- 1 cup sugar\\n- 1/2 cup butter, softened\\n- 2 eggs\\n\\nInstructions:\\n1. Preheat oven to 350°F\\n2. Mix all ingredients\\n3. Bake for 10-12 minutes\\n\\nPrep time: 15 minutes\\nCook time: 12 minutes\\nServings: 24 cookies"
}
```

**Response:**
```json
{
  "recipe": {
    "title": "Chocolate Chip Cookies",
    "description": null,
    "ingredients": [
      {"name": "flour", "quantity": "2 cups", "preparation": null},
      {"name": "sugar", "quantity": "1 cup", "preparation": null},
      {"name": "butter", "quantity": "1/2 cup", "preparation": "softened"},
      {"name": "eggs", "quantity": "2", "preparation": null}
    ],
    "instructions": [
      "Preheat oven to 350°F",
      "Mix all ingredients",
      "Bake for 10-12 minutes"
    ],
    "prep_time": "15 minutes",
    "cook_time": "12 minutes",
    "servings": "24 cookies"
  },
  "confidence": 0.92
}
```

### 4. Extract Event Information

**POST** `/extract/event`

Extract event details from text.

**Request Body:**
```json
{
  "text": "Team Meeting scheduled for January 15, 2024 at 2:00 PM in Conference Room A. Jane Smith is organizing. Attendees include John Doe and Alice Johnson."
}
```

**Response:**
```json
{
  "events": [
    {
      "title": "Team Meeting",
      "description": null,
      "date": "January 15, 2024",
      "time": "2:00 PM",
      "location": "Conference Room A",
      "organizer": "Jane Smith",
      "attendees": ["John Doe", "Alice Johnson"]
    }
  ],
  "confidence": 0.88
}
```

### 5. Extract Product Information

**POST** `/extract/product`

Extract product details from descriptions.

**Request Body:**
```json
{
  "text": "Wireless Headphones by AudioTech - $99.99. Premium wireless headphones with active noise cancellation. Features: Bluetooth 5.0, 30-hour battery life, comfortable ear cushions. Weight: 250g."
}
```

**Response:**
```json
{
  "products": [
    {
      "name": "Wireless Headphones",
      "category": "electronics",
      "price": "$99.99",
      "brand": "AudioTech",
      "description": "Premium wireless headphones with active noise cancellation",
      "features": ["Bluetooth 5.0", "30-hour battery life", "comfortable ear cushions"],
      "specifications": {"weight": "250g"}
    }
  ],
  "confidence": 0.90
}
```

### 6. Analyze Sentiment

**POST** `/extract/sentiment`

Analyze sentiment from text.

**Request Body:**
```json
{
  "text": "I absolutely love this product! The quality is amazing and shipping was super fast. The only downside is that it's a bit expensive, but totally worth it for the quality."
}
```

**Response:**
```json
{
  "analysis": {
    "sentiment": "positive",
    "confidence": 0.95,
    "positive_aspects": ["Amazing quality", "Fast shipping", "Worth the price"],
    "negative_aspects": ["Expensive"],
    "summary": "Overall very positive review with minor price concern, but customer finds it worth the cost"
  }
}
```

## Usage Examples

### Using cURL

```bash
# Extract contact information
curl -X POST http://localhost:8000/extract/contact \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact Sarah Johnson at sarah.j@techcorp.com or call +1-555-987-6543"
  }'

# Extract recipe
curl -X POST http://localhost:8000/extract/recipe \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Pancakes: Mix 2 cups flour, 2 eggs, 1 cup milk. Cook on griddle for 2-3 minutes per side. Serves 4."
  }'

# Extract event
curl -X POST http://localhost:8000/extract/event \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Annual Conference on March 20th at 9 AM, Grand Hotel, organized by Marketing Team"
  }'

# Extract product
curl -X POST http://localhost:8000/extract/product \
  -H "Content-Type: application/json" \
  -d '{
    "text": "SmartWatch Pro by TechGear - $299. Features GPS, heart rate monitor, waterproof design."
  }'

# Analyze sentiment
curl -X POST http://localhost:8000/extract/sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Terrible experience. Product broke after one week and customer service was unhelpful."
  }'
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# Extract contact information
response = requests.post(
    f"{base_url}/extract/contact",
    json={
        "text": "Reach out to Dr. Emily Chen at emily.chen@university.edu, office phone: (555) 234-5678"
    }
)
contact_data = response.json()
print(f"Name: {contact_data['contacts'][0]['name']}")
print(f"Email: {contact_data['contacts'][0]['email']}")
print(f"Confidence: {contact_data['confidence']}")

# Extract recipe
response = requests.post(
    f"{base_url}/extract/recipe",
    json={
        "text": """
        Easy Pasta Recipe

        Ingredients:
        - 1 lb pasta
        - 2 cups tomato sauce
        - 1/2 cup parmesan cheese, grated
        - 2 cloves garlic, minced

        Instructions:
        1. Boil pasta according to package directions
        2. Heat sauce with garlic
        3. Combine pasta and sauce
        4. Top with parmesan

        Prep: 10 min, Cook: 15 min, Serves: 4
        """
    }
)
recipe_data = response.json()
print(f"Recipe: {recipe_data['recipe']['title']}")
print(f"Ingredients: {len(recipe_data['recipe']['ingredients'])}")
print(f"Steps: {len(recipe_data['recipe']['instructions'])}")

# Analyze sentiment
response = requests.post(
    f"{base_url}/extract/sentiment",
    json={
        "text": "Mixed feelings about this. Great design and user-friendly, but battery life could be better."
    }
)
sentiment_data = response.json()
print(f"Sentiment: {sentiment_data['analysis']['sentiment']}")
print(f"Positive: {sentiment_data['analysis']['positive_aspects']}")
print(f"Negative: {sentiment_data['analysis']['negative_aspects']}")
```

## Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html
```

## How It Works

### OpenAI Function Calling Flow

1. **Define Pydantic Model**: Create a model with desired fields
2. **Convert to Function Schema**: Automatically convert Pydantic model to OpenAI function schema
3. **Call OpenAI**: Send text + function schema to OpenAI
4. **Extract Arguments**: OpenAI returns function call with arguments
5. **Validate with Pydantic**: Parse arguments into Pydantic model (automatic validation)
6. **Return Structured Data**: Type-safe, validated data ready to use

```
User Text
    ↓
[Pydantic Model] → [OpenAI Function Schema]
    ↓
[OpenAI API Call]
    ↓
[Function Call Response with JSON arguments]
    ↓
[Pydantic Validation]
    ↓
Structured, Validated Data
```

### Example: Contact Extraction

```python
# 1. Define Pydantic model
class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Person's full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")

# 2. Convert to function schema (automatic)
function_schema = {
    "name": "extract_contact_info",
    "description": "Extract contact information from text",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Person's full name"},
            "email": {"type": "string", "description": "Email address"},
            "phone": {"type": "string", "description": "Phone number"}
        }
    }
}

# 3. Call OpenAI with function
response = openai.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[{"role": "user", "content": "Contact John at john@example.com"}],
    functions=[function_schema],
    function_call={"name": "extract_contact_info"}
)

# 4. Parse and validate
arguments = json.loads(response.choices[0].message.function_call.arguments)
contact = ContactInfo(**arguments)  # Pydantic validates!

# 5. Use structured data
print(contact.name)   # "John"
print(contact.email)  # "john@example.com"
```

## Key Concepts

### 1. Pydantic Models

Pydantic models define the structure of extracted data:

```python
class Recipe(BaseModel):
    title: str = Field(..., description="Recipe title")
    ingredients: List[Ingredient] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=list)
    prep_time: Optional[str] = Field(None, description="Prep time")
```

Benefits:
- **Type safety**: Enforce types at runtime
- **Validation**: Automatic validation of all fields
- **Documentation**: Field descriptions help OpenAI understand what to extract
- **Optional fields**: Handle incomplete data gracefully

### 2. OpenAI Function Calling

OpenAI's function calling feature allows:
- **Structured outputs**: LLM returns data in specific format
- **Reliability**: More reliable than parsing free-form text
- **Type awareness**: LLM knows expected types
- **Multiple functions**: Can choose between multiple extraction types

### 3. Confidence Scoring

Confidence is calculated based on field completion:

```python
total_fields = len(model.model_fields)
filled_fields = count_non_empty_fields(data)
confidence = filled_fields / total_fields
```

Higher confidence means more complete extraction.

### 4. Schema Generation

Pydantic models are automatically converted to OpenAI function schemas:

```python
# Pydantic model
class Product(BaseModel):
    name: str
    price: Optional[str]

# Becomes OpenAI function schema
{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "price": {"type": "string"}
    },
    "required": ["name"]
}
```

## Differences from Previous POCs

| Feature | POC 1 (Basic API) | POC 2 (Chatbot) | POC 3 (Document QA) | POC 4 (Structuring) |
|---------|------------------|-----------------|---------------------|---------------------|
| Output Format | Free text | Free text | Free text | Structured JSON |
| Validation | None | None | None | Pydantic models |
| Type Safety | No | No | No | Yes |
| Function Calling | No | No | No | Yes |
| Use Case | Chat | Conversations | Q&A | Data extraction |
| Reliability | Variable | Variable | Variable | High |

## Use Cases

### 1. Contact Extraction
- **Email parsing**: Extract senders, recipients from emails
- **Business cards**: Digitize contact information
- **Customer data**: Parse support tickets for contact details

### 2. Recipe Extraction
- **Recipe websites**: Structure recipes from blog posts
- **Cookbooks**: Digitize print recipes
- **Social media**: Extract recipes from posts

### 3. Event Extraction
- **Email invites**: Parse meeting invites
- **Calendar entries**: Extract event details
- **Event listings**: Structure event information

### 4. Product Extraction
- **E-commerce**: Parse product descriptions
- **Reviews**: Extract product details from reviews
- **Catalogs**: Digitize product catalogs

### 5. Sentiment Analysis
- **Reviews**: Analyze customer reviews
- **Social media**: Monitor brand sentiment
- **Feedback**: Categorize customer feedback

## Limitations

1. **API costs**: Each extraction requires OpenAI API call
2. **Model limitations**: Quality depends on LLM capabilities
3. **Complex nested structures**: Very deep nesting may be challenging
4. **Ambiguous text**: Unclear text leads to lower confidence
5. **No context**: Each extraction is independent

## Next Steps

After completing this POC, consider:
1. Adding batch extraction for multiple items
2. Implementing custom validation rules
3. Adding retry logic with exponential backoff
4. Implementing caching for common extractions
5. Adding support for images (OCR + extraction)
6. Combining with RAG for context-aware extraction
7. Creating custom extraction types for your domain

## Troubleshooting

### Common Issues

1. **"Invalid API key"**
   - Check `.env` file has correct `OPENAI_API_KEY`
   - Ensure API key is active and has credits

2. **Low confidence scores**
   - Text may be ambiguous or incomplete
   - Adjust Pydantic model to match available data
   - Make optional fields for uncertain data

3. **Validation errors**
   - Check Pydantic model constraints
   - Review field types and requirements
   - Enable debug logging to see raw extraction

4. **Slow extractions**
   - OpenAI API calls take 1-3 seconds
   - Consider caching for repeated queries
   - Use batch processing for multiple items

5. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## Performance Considerations

- **API latency**: ~1-3 seconds per extraction
- **Token costs**: Depends on input text length
- **Rate limits**: OpenAI has rate limits (RPM, TPM)
- **Concurrent requests**: FastAPI handles multiple requests in parallel

## Security Notes

- Never commit `.env` file with real API keys
- Sanitize user inputs before sending to OpenAI
- Implement rate limiting for API endpoints
- Consider PII in extracted data
- Validate all extracted data before using

## Resources

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## License

MIT License - See root repository for details.
