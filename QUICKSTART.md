# 🚀 Quick Start Guide

Get the Seti backend API up and running in minutes!

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- **Supabase account** (sign up free at https://supabase.com)

## 1. Setup Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Setup Supabase Database

### Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Name: `seti-prediction-markets`
4. Generate a strong database password (save it!)
5. Choose a region
6. Click **"Create new project"**

### Get Your Credentials

1. In Supabase dashboard, go to **Settings** > **Database**
2. Copy the **Connection string** (URI format)
3. Go to **Settings** > **API**
4. Copy **Project URL**, **anon key**, and **service_role key**

### Configure Environment

```bash
# Copy Supabase example
cp .env.supabase.example .env

# Edit with your Supabase credentials
nano .env
```

Replace with your actual values:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_REF.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR_REF.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SERVICE_KEY
```

**📖 For detailed setup, see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)**

## 4. Initialize Database

```bash
# Create database tables
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# (Optional) Seed with sample data
python scripts/seed_data.py
```

## 5. Run the Server

```bash
python run.py
```

The API will be available at: **http://localhost:5000**

## 6. Test the API

Open your browser or use curl:

```bash
# Health check
curl http://localhost:5000/health

# Get markets
curl http://localhost:5000/api/v1/markets

# Get analytics
curl http://localhost:5000/api/v1/analytics/overview
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/markets` | GET | List all markets |
| `/api/v1/markets/<id>` | GET | Get single market |
| `/api/v1/predictions` | GET | List predictions |
| `/api/v1/users/<address>` | GET | Get user profile |
| `/api/v1/analytics/overview` | GET | Platform statistics |

Full API documentation is available in [README.md](./README.md)

## Using Docker (Alternative)

If you prefer Docker:

```bash
# Start all services (backend, postgres, redis)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Connecting Frontend

Update your frontend `.env` file:

```env
VITE_API_URL=http://localhost:5000/api/v1
```

## Troubleshooting

### Port already in use
```bash
# Change port in .env
echo "PORT=5001" >> .env
```

### Database errors
```bash
# Reset database
rm seti.db
python scripts/init_db.py
```

### Import errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

- Read the full [README.md](./README.md) for detailed API documentation
- Check [config/settings.py](./config/settings.py) for configuration options
- Explore the API routes in [app/api/](./app/api/)
- Review database models in [app/models/](./app/models/)

## Support

For issues, please check the main README or create an issue on GitHub.

Happy coding! 🎉

