# Person Advisor API

AI-powered guidance on how to deal with people in your life. Get personalized advice, rewrite messages, and have meaningful conversations about your relationships.

## Features

- 🤖 **AI-Powered Insights**: Generate personality traits and guidance using OpenAI GPT-4
- 💬 **Smart Conversations**: Chat with an AI advisor about people in your life
- ✍️ **Message Rewriting**: Improve your messages with key improvements and suggestions
- 📊 **Personality Analysis**: Answer questionnaires to understand people better
- 📈 **Recent Interactions**: Track your recent conversations with different people
- ⭐ **Ratings System**: Rate your interactions and experiences

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (with Motor for async)
- **AI**: OpenAI GPT-4o
- **ORM**: Beanie (MongoDB ODM)
- **Server**: Uvicorn

## Prerequisites

- Python 3.11+
- MongoDB Atlas account (or local MongoDB)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd person-advisor-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
   DB_NAME=dominicember555
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload --port 7000
   ```

Visit `http://localhost:7000/docs` for the interactive API documentation.

## API Endpoints

### Profiles
- `POST /profiles/` - Create a person profile
- `GET /profiles/{profile_id}` - Get profile details
- `PATCH /profiles/{profile_id}` - Update profile
- `DELETE /profiles/{profile_id}` - Delete profile
- `GET /profiles/user/{user_id}` - Get all profiles for a user

### Questionnaire
- `GET /profiles/{profile_id}/questions` - Get personality questionnaire
- `POST /profiles/{profile_id}/answers` - Submit questionnaire answers

### Guidance
- `GET /profiles/{profile_id}/guidance` - Get AI guidance for a person
- `GET /profiles/{profile_id}/traits` - Get extracted personality traits

### Conversations
- `POST /profiles/{profile_id}/chat` - Send a message and get AI response
- `GET /profiles/{profile_id}/conversations` - Get conversation history
- `GET /profiles/user/{user_id}/recent` - Get recent interactions

### Message Rewriting
- `POST /messages/rewrite` - Rewrite a message with improvements and suggestions

### Ratings
- `POST /profiles/{profile_id}/ratings` - Submit a rating
- `GET /profiles/{profile_id}/ratings/average` - Get average rating

## Request/Response Examples

### Create Profile
```bash
POST /profiles/
{
  "user_id": "507f1f77bcf86cd799439011",
  "name": "Sarah",
  "relationship": "Manager",
  "description": "My direct manager, very strict with deadlines"
}
```

### Submit Questionnaire Answers
```bash
POST /profiles/{profile_id}/answers
{
  "answers": [
    {
      "question": "How does Sarah typically communicate?",
      "selected_option": "Direct and straightforward"
    }
  ]
}
```

### Chat Endpoint
```bash
POST /profiles/{profile_id}/chat?user_id=user123
{
  "content": "How should I approach Sarah about the deadline extension?"
}
```

### Rewrite Message
```bash
POST /messages/rewrite
{
  "message": "hey can u help me plz",
  "context": "talking to my manager"
}
```

### Get Recent Interactions
```bash
GET /profiles/user/{user_id}/recent
```

Response:
```json
{
  "interactions": [
    {
      "conversation_id": "507f1f77bcf86cd799439011",
      "profile_id": "507f1f77bcf86cd799439012",
      "person_name": "Sarah",
      "relationship": "Manager",
      "last_message": "Thanks for your help with the project...",
      "last_message_time": "2026-04-11T18:30:00",
      "message_count": 12
    }
  ],
  "total": 1
}
```

## Project Structure

```
person-advisor-api/
├── app/
│   ├── models/              # Database models (Beanie Documents)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic and AI calls
│   ├── utils/               # Helpers and exceptions
│   ├── config.py            # Configuration
│   └── database.py          # Database setup
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `MONGODB_URL` - MongoDB connection string
- `DB_NAME` - Database name

### Security Notes

⚠️ Never commit `.env` file to git. It contains sensitive credentials.

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
black app/
flake8 app/
```

## Deployment

### Docker
```bash
docker build -t person-advisor-api .
docker run -p 7000:7000 --env-file .env person-advisor-api
```

### Production Server
For production, use a proper ASGI server like Gunicorn with Uvicorn workers:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Disabled Endpoints

The following endpoints are currently disabled and require backend integration:
- `POST /users/` - User creation (disabled)

These endpoints are managed externally and the API expects `user_id` to be provided from the frontend or another backend service.

## Error Handling

The API returns standardized error responses:

```json
{
  "error": true,
  "status_code": 400,
  "message": "Invalid ID format: xyz"
}
```

Common status codes:
- `400` - Bad request or invalid input
- `404` - Resource not found
- `500` - Server error (often from OpenAI API)

## Troubleshooting

### Empty response from OpenAI API
Check that your OpenAI API key is valid and has credits available.

### MongoDB connection error
Verify your `MONGODB_URL` and ensure your IP is whitelisted in MongoDB Atlas.

### Invalid JSON from OpenAI
The API automatically cleans up markdown code blocks. If errors persist, check the response in logs.

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, create a GitHub issue or contact the development team.

---

**Last Updated**: April 11, 2026
**Version**: 1.0.0