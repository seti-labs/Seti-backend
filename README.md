# 🔮 Seti Backend API

Flask-based backend API for the Seti prediction market platform. Provides RESTful endpoints for market data, user profiles, predictions, and analytics.

## 🚀 Features

- **Market Management**: Index and serve market data from Sui blockchain
- **User Profiles**: Track user activity, predictions, and statistics
- **Predictions API**: Record and query user predictions
- **Analytics**: Platform-wide statistics and insights
- **Caching**: Redis-based caching for optimal performance
- **Database**: PostgreSQL/SQLite for data persistence

## 📋 Prerequisites

- Python 3.9+
- **Supabase account** (recommended) or PostgreSQL/SQLite for development
- Redis (optional, for caching)

## 🛠️ Installation

### 1. Clone and Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

#### Using Supabase (Recommended)

```bash
cp .env.supabase.example .env
```

Edit `.env` with your Supabase credentials:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Supabase Database
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Supabase API
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]
SUPABASE_SERVICE_KEY=[YOUR-SERVICE-ROLE-KEY]

# Sui Blockchain
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**📖 For detailed Supabase setup instructions, see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)**

#### Using Local PostgreSQL or SQLite

```bash
cp .env.example .env
# Edit with local database URL
```

### 3. Database Setup

```bash
# Initialize database
flask db init

# Create migrations
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

### 4. Run the Server

```bash
# Development
python run.py

# Or with Flask CLI
flask run
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Markets

#### Get All Markets
```http
GET /api/v1/markets?page=1&per_page=20&category=Crypto&status=active&sort_by=volume_24h
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)
- `category`: Filter by category (optional)
- `status`: `active` or `resolved` (optional)
- `sort_by`: `volume_24h`, `total_liquidity`, `created_timestamp` (default: `created_timestamp`)
- `search`: Search in question/description (optional)

**Response:**
```json
{
  "markets": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Single Market
```http
GET /api/v1/markets/<market_id>
```

#### Get Featured Markets
```http
GET /api/v1/markets/featured
```

#### Get Categories
```http
GET /api/v1/markets/categories
```

#### Sync Markets from Blockchain
```http
POST /api/v1/markets/sync
```

### Predictions

#### Get Predictions
```http
GET /api/v1/predictions?market_id=0x123...&user_address=0xabc...
```

**Query Parameters:**
- `page`: Page number
- `per_page`: Items per page
- `market_id`: Filter by market (optional)
- `user_address`: Filter by user (optional)
- `outcome`: Filter by outcome (0 or 1) (optional)

#### Create Prediction
```http
POST /api/v1/predictions
Content-Type: application/json

{
  "transaction_hash": "0x...",
  "market_id": "0x...",
  "user_address": "0x...",
  "outcome": 1,
  "amount": 1000000000,
  "price": 550000000,
  "shares": 500000000,
  "timestamp": 1234567890
}
```

#### Get Recent Predictions
```http
GET /api/v1/predictions/recent?limit=50
```

### Users

#### Get User Profile
```http
GET /api/v1/users/<address>
```

#### Update User Profile
```http
PUT /api/v1/users/<address>
Content-Type: application/json

{
  "username": "trader123",
  "email": "trader@example.com",
  "avatar_url": "https://...",
  "bio": "Prediction market enthusiast"
}
```

#### Get User Predictions
```http
GET /api/v1/users/<address>/predictions
```

#### Get User Statistics
```http
GET /api/v1/users/<address>/stats
```

#### Get Leaderboard
```http
GET /api/v1/users/leaderboard?sort_by=total_volume&limit=50
```

### Analytics

#### Get Platform Overview
```http
GET /api/v1/analytics/overview
```

**Response:**
```json
{
  "overview": {
    "total_markets": 150,
    "active_markets": 120,
    "resolved_markets": 30,
    "total_volume": 50000000000000,
    "total_liquidity": 10000000000000,
    "total_predictions": 5000,
    "total_users": 500,
    "active_users_7d": 150
  }
}
```

#### Get Top Markets
```http
GET /api/v1/analytics/markets/top?metric=volume&limit=10
```

**Metrics:** `volume`, `liquidity`, `predictions`

#### Get Category Statistics
```http
GET /api/v1/analytics/categories/stats
```

#### Get Recent Activity
```http
GET /api/v1/analytics/activity/recent?limit=20
```

### Health Check

```http
GET /health
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py           # App factory
│   ├── api/                  # API routes
│   │   ├── markets.py
│   │   ├── predictions.py
│   │   ├── users.py
│   │   └── analytics.py
│   ├── models/               # Database models
│   │   ├── market.py
│   │   ├── prediction.py
│   │   └── user.py
│   ├── services/             # Business logic
│   │   └── sui_service.py
│   └── utils/                # Utilities
│       ├── helpers.py
│       └── validators.py
├── config/
│   └── settings.py           # Configuration
├── migrations/               # Database migrations
├── requirements.txt
├── run.py                    # Application entry point
└── README.md
```

## 🔧 Database Models

### Market
- Stores cached market data from blockchain
- Includes liquidity, shares, volume, and metadata
- Calculates YES/NO prices dynamically

### Prediction
- Records user predictions/trades
- Links to markets and users
- Tracks amounts, outcomes, and timestamps

### User
- User profiles and statistics
- Aggregates prediction counts and volumes
- Tracks activity timestamps

## 🚀 Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SUI_NETWORK=mainnet
SUI_RPC_URL=https://fullnode.mainnet.sui.io:443
```

## 🧪 Testing

```bash
# Run tests
python -m pytest

# With coverage
python -m pytest --cov=app
```

## 📊 Caching Strategy

- Market lists: 60 seconds
- Single market: 30 seconds
- Categories: 5 minutes
- Analytics: 5 minutes
- User stats: 2 minutes

## 🔐 Security Considerations

- Use strong `SECRET_KEY` in production
- Enable HTTPS/TLS
- Implement rate limiting
- Validate all user inputs
- Sanitize database queries
- Keep dependencies updated

## 📝 Development

### Adding a New Endpoint

1. Create route in appropriate blueprint (`app/api/`)
2. Add business logic to service layer if needed
3. Update models if database changes required
4. Create migration: `flask db migrate -m "description"`
5. Apply migration: `flask db upgrade`

### Database Migrations

```bash
# Create migration
flask db migrate -m "Add new field"

# Apply migration
flask db upgrade

# Rollback
flask db downgrade
```

## 🤝 Integration with Frontend

The frontend should point to this backend:

```typescript
// In frontend .env
VITE_API_URL=http://localhost:5000/api/v1
```

## 📄 License

MIT License - see LICENSE file for details

## 👥 Support

For issues and questions:
- GitHub Issues: [repository link]
- Email: support@seti.app

---

Built with ❤️ for the Sui ecosystem

