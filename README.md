# 🔮 Seti Backend API

Flask-based backend for the Seti prediction market platform with **Web2.5 architecture**: fast database queries + blockchain settlement.

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment (recommended but optional)
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install packages
pip3 install --user -r requirements.txt
```

### 2. Choose Your Database

**Option A: SQLite (Quick Testing)**
```bash
# Create .env
cat > .env << 'EOF'
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///seti.db
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
PORT=5001
HOST=0.0.0.0
EOF

# Initialize database
python3 scripts/init_db.py
```

**Option B: Supabase (Production)**
```bash
# Get credentials from https://supabase.com/dashboard
# Settings > Database > Connection string (URI)
# Settings > API > Project URL, anon key, service_role key

cat > .env << 'EOF'
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_REF.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR_REF.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SERVICE_KEY
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080
PORT=5001
HOST=0.0.0.0
EOF

# Run SQL schema in Supabase SQL Editor (copy from supabase_schema.sql)
```

### 3. Seed Sample Data

```bash
python3 scripts/seed_data.py
python3 scripts/add_predictions.py
```

### 4. Start Backend

```bash
python3 run.py
```

✅ API running at **http://localhost:5001**

### 5. Test

```bash
curl http://localhost:5001/health
curl http://localhost:5001/api/v1/markets
```

---

## 📡 API Endpoints

### Markets
```bash
GET    /api/v1/markets                    # List markets (filter, search, paginate)
GET    /api/v1/markets/:id                # Single market
GET    /api/v1/markets/featured           # Featured markets
GET    /api/v1/markets/categories         # Categories with counts
POST   /api/v1/markets/sync               # Sync from blockchain
```

**Query params:** `page`, `per_page`, `category`, `status`, `sort_by`, `search`

### Predictions
```bash
GET    /api/v1/predictions                # List predictions
GET    /api/v1/predictions/:id            # Single prediction
POST   /api/v1/predictions                # Record new prediction
GET    /api/v1/predictions/recent         # Recent activity
```

### Users
```bash
GET    /api/v1/users/:address             # User profile
PUT    /api/v1/users/:address             # Update profile
GET    /api/v1/users/:address/predictions # User's predictions
GET    /api/v1/users/:address/stats       # User statistics
GET    /api/v1/users/leaderboard          # Top traders
```

### Analytics
```bash
GET    /api/v1/analytics/overview         # Platform stats
GET    /api/v1/analytics/markets/top      # Top markets
GET    /api/v1/analytics/categories/stats # Category breakdown
GET    /api/v1/analytics/activity/recent  # Recent activity
```

---

## 🗄️ Database Schema

**9 Tables (Web2.5 Architecture):**

1. **markets** - Market data from blockchain + engagement metrics
2. **predictions** - Transaction history
3. **users** - Rich profiles (username, avatar, stats, gamification)
4. **liquidity_providers** - LP tracking
5. **liquidity_withdrawals** - LP withdrawal history
6. **comments** - Social layer (discussions, replies)
7. **favorites** - User watchlists
8. **notifications** - User notifications
9. **activity_feed** - Platform-wide activity

### What's Stored

✅ **All blockchain data** (cached for speed)
- Markets, predictions, liquidity, resolutions

✅ **Web2 enhancements** (not on blockchain)
- User profiles (username, avatar, bio)
- Comments and discussions
- Favorites/watchlists
- Notifications
- View counts, trending scores
- Analytics and aggregations

---

## 🔗 Frontend Integration

### Setup Frontend

```bash
# In frontend directory
cat > .env.local << 'EOF'
VITE_API_URL=http://localhost:5001/api/v1
VITE_SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
VITE_NETWORK=devnet
VITE_SUI_RPC_URL=https://fullnode.devnet.sui.io:443
EOF
```

### API Service (Frontend)

```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL;

export const marketsApi = {
  getAll: (params) => fetch(`${API_BASE_URL}/markets?${new URLSearchParams(params)}`),
  getById: (id) => fetch(`${API_BASE_URL}/markets/${id}`),
};

// Usage in React
const { markets } = await marketsApi.getAll({ category: 'Crypto' });
```

### Sync Blockchain Transactions

```typescript
// After blockchain transaction succeeds
await fetch('http://localhost:5001/api/v1/predictions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    transaction_hash: txResult.digest,
    market_id: marketId,
    user_address: currentUser.address,
    outcome: 1, // YES
    amount: 1000000000,
    timestamp: Math.floor(Date.now() / 1000)
  })
});
```

---

## 🌐 Web2.5 Architecture

```
┌──────────────┐
│   Frontend   │ (React, fast UX)
└──────┬───────┘
       │
       ├─────────────┬─────────────┐
       ↓             ↓             ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Backend  │  │   Sui    │  │ Wallet   │
│   API    │  │Blockchain│  │  (Sign)  │
└─────┬────┘  └──────────┘  └──────────┘
      │
      ↓
┌──────────┐
│ Supabase │
│ Database │
└──────────┘
```

**User Flow:**
1. User places bet → Signs with wallet → Blockchain confirms ✅
2. Frontend → Backend API → Stores in database instantly 🚀
3. User sees update immediately (no blockchain query needed) ⚡
4. Social features (comments, favorites) → Database only 💬

**Benefits:**
- ⚡ Fast as traditional web apps
- 🔒 Secured by blockchain
- 🎯 Rich features (search, analytics, social)
- 📊 Better UX than pure Web3

---

## 🛠️ Troubleshooting

### Port 5000 Already in Use
macOS AirPlay uses port 5000. Use port 5001 instead (already configured).

### CORS Errors
Add your frontend URL to `CORS_ORIGINS` in `.env`

### Database Connection Failed (Supabase)
- Check `DATABASE_URL` password is correct
- Verify project reference in URL
- Ensure Supabase project is active

### No Markets Showing
Run seed scripts:
```bash
python3 scripts/seed_data.py
python3 scripts/add_predictions.py
```

### Import Errors
```bash
pip3 install --user -r requirements.txt
```

---

## 🚀 Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5001 run:app
```

### Using Docker

```bash
docker-compose up -d
```

### Environment Variables (Production)

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=<supabase-connection-string>
CORS_ORIGINS=https://yourdomain.com
```

---

## 📊 Data Flow Example

**Creating a Prediction:**

1. **Frontend** → User clicks "Place Bet"
2. **Wallet** → Signs blockchain transaction
3. **Blockchain** → Processes transaction, confirms
4. **Frontend** → Calls backend API:
   ```bash
   POST /api/v1/predictions
   { transaction_hash, market_id, user_address, outcome, amount }
   ```
5. **Backend** → Stores in database
6. **Frontend** → Instantly shows updated UI (from database, not blockchain)

**Result:** Users get instant feedback + blockchain security! 🎉

---

## 🎯 Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── api/                     # API routes
│   │   ├── markets.py           # Market endpoints
│   │   ├── predictions.py       # Prediction endpoints
│   │   ├── users.py             # User endpoints
│   │   └── analytics.py         # Analytics endpoints
│   ├── models/                  # Database models
│   │   ├── market.py
│   │   ├── prediction.py
│   │   ├── user.py
│   │   ├── liquidity.py
│   │   ├── comment.py
│   │   └── notification.py
│   ├── services/                # Business logic
│   │   ├── sui_service.py       # Blockchain integration
│   │   └── supabase_service.py  # Supabase features
│   └── utils/                   # Utilities
│       ├── helpers.py
│       └── validators.py
├── config/
│   └── settings.py              # Configuration
├── scripts/
│   ├── init_db.py              # Database initialization
│   ├── seed_data.py            # Sample data
│   └── add_predictions.py      # Add predictions
├── supabase_schema.sql         # Supabase SQL schema
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
├── Dockerfile
├── docker-compose.yml
└── README.md                   # This file
```

---

## 📚 Tech Stack

- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** (Supabase) - Database
- **Flask-CORS** - CORS handling
- **Flask-Caching** - Response caching
- **Supabase** - Database + realtime + storage

---

## 📄 License

MIT License - see LICENSE file

---

## 🆘 Support

**Backend running?**
```bash
curl http://localhost:5001/health
# Expected: {"status": "healthy", "service": "seti-backend"}
```

**Check logs:** Backend outputs to console

**Database issues:** Check `.env` file configuration

**Still stuck?** Create an issue on GitHub

---

## ✅ Success Checklist

- [ ] Backend running on port 5001
- [ ] Database configured (SQLite or Supabase)
- [ ] Sample data seeded
- [ ] API responds to `/health`
- [ ] Markets endpoint returns data
- [ ] Frontend `.env.local` configured
- [ ] CORS enabled for your frontend port
- [ ] No errors in browser console

---

**Built with ❤️ for the Sui ecosystem**

🚀 **Your Web2.5 prediction market backend is ready!**
