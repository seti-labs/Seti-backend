# 🌐 Web2.5 Architecture - Complete Data Storage

## Philosophy

**Web2.5 = Web2 UX + Web3 Settlement**

- ✅ Store EVERYTHING in database for fast queries
- ✅ Blockchain only for transactions and settlement
- ✅ Users get instant, smooth experience
- ✅ Blockchain provides trust and immutability

## 📊 Complete Database Schema

### 1. **Markets** (Core Trading Data)
```python
✅ Blockchain data (cached):
  - Market ID, question, description
  - Creator address
  - End time, created timestamp
  - Total liquidity, share counts
  - Volume 24h
  - Resolved status, winning outcome
  - Category, tags, image URL

✅ Web2 enhancements:
  - View count (how many people viewed)
  - Participant count (unique traders)
  - Comment count
  - Favorite count
  - Slug (SEO-friendly URLs)
  - Featured flag
  - Trending score
  - Last updated timestamp
```

### 2. **Predictions** (Transaction History)
```python
✅ All user trades:
  - Transaction hash (blockchain reference)
  - Market ID
  - User wallet address
  - Outcome (YES/NO)
  - Amount in SUI
  - Price at time of trade
  - Shares received
  - Timestamp
```

### 3. **Users** (Rich Profiles)
```python
✅ Profile data:
  - Wallet address
  - Username (custom display name)
  - Email (optional, for notifications)
  - Avatar URL
  - Bio/description

✅ Trading stats:
  - Total predictions count
  - Total volume traded
  - Markets created
  - Win count / Loss count
  - Total P&L (profit/loss)

✅ Social:
  - Follower count
  - Following count

✅ Gamification:
  - Level (1-100)
  - Experience points
  - Badges array
  
✅ Preferences:
  - Notification settings
  - Theme (light/dark/system)

✅ Status:
  - First seen date
  - Last active timestamp
  - Verified status
  - Banned status
```

### 4. **Liquidity Providers** (LP Tracking)
```python
✅ Track who provides liquidity:
  - Transaction hash
  - Market ID
  - Provider wallet address
  - Amount provided
  - LP shares received
  - Timestamp
  - Withdrawn status
```

### 5. **Liquidity Withdrawals**
```python
✅ Track LP withdrawals:
  - Transaction hash
  - Market ID
  - Provider address
  - Amount withdrawn
  - Timestamp
```

### 6. **Comments** (Social Layer)
```python
✅ User discussions on markets:
  - Market ID
  - User address
  - Comment content
  - Parent comment ID (for replies/threads)
  - Like count
  - Created/updated timestamps
```

### 7. **Favorites** (Watchlist)
```python
✅ Users can favorite markets:
  - User address
  - Market ID
  - Created timestamp
```

### 8. **Notifications**
```python
✅ User notifications:
  - User address
  - Type (market_resolved, won_prediction, reply, etc.)
  - Title and message
  - Link to relevant page
  - Read status
  - Created timestamp
```

### 9. **Activity Feed**
```python
✅ Platform-wide activity stream:
  - Activity type (market_created, prediction_placed, market_resolved)
  - User address
  - Market ID
  - Prediction ID
  - Additional JSON data
  - Timestamp
```

## 🔄 Data Flow

### When User Places a Bet

```
1. Frontend → Blockchain
   User signs transaction with wallet
   
2. Blockchain confirms
   Transaction processed on Sui
   
3. Frontend → Backend API
   POST /api/v1/predictions
   {
     transaction_hash: "0x123...",
     market_id: "0xmarket...",
     user_address: "0xuser...",
     outcome: 1,  // YES
     amount: 1000000000  // 1 SUI in MIST
   }
   
4. Backend stores in database
   ✅ Create prediction record
   ✅ Update market stats
   ✅ Update user stats
   ✅ Create activity feed entry
   ✅ Notify followers
   
5. Frontend refreshes from Backend
   ✅ Instant UI update
   ✅ No blockchain query needed
```

### When User Comments

```
1. Frontend → Backend API
   POST /api/v1/comments
   {
     market_id: "0xmarket...",
     user_address: "0xuser...",
     content: "I think YES will win!"
   }
   
2. Backend stores
   ✅ Create comment record
   ✅ Update market comment count
   ✅ Create activity feed entry
   ✅ Notify market participants
   
3. Frontend shows immediately
   ✅ No blockchain needed!
```

### When User Adds to Watchlist

```
1. Frontend → Backend API
   POST /api/v1/favorites
   
2. Backend stores
   ✅ Create favorite record
   ✅ Update market favorite count
   
3. User's watchlist updated instantly
```

## 📡 API Endpoints (Complete)

### Markets
```
GET    /api/v1/markets                    # List all (with search/filter)
GET    /api/v1/markets/:id                # Get single market
POST   /api/v1/markets                    # Create (from blockchain sync)
PUT    /api/v1/markets/:id                # Update stats
GET    /api/v1/markets/:id/comments       # Get comments
GET    /api/v1/markets/:id/participants   # Get traders
POST   /api/v1/markets/:id/view           # Increment view count
```

### Predictions
```
GET    /api/v1/predictions                # List all
POST   /api/v1/predictions                # Record new prediction
GET    /api/v1/predictions/recent         # Recent activity
```

### Users
```
GET    /api/v1/users/:address             # Get profile
PUT    /api/v1/users/:address             # Update profile
GET    /api/v1/users/:address/predictions # Trading history
GET    /api/v1/users/:address/stats       # Detailed stats
GET    /api/v1/users/:address/favorites   # Watchlist
POST   /api/v1/users/:address/follow      # Follow user
GET    /api/v1/users/:address/followers   # Get followers
GET    /api/v1/users/leaderboard          # Top traders
```

### Comments
```
GET    /api/v1/comments                   # Get comments (by market)
POST   /api/v1/comments                   # Add comment
PUT    /api/v1/comments/:id               # Edit comment
DELETE /api/v1/comments/:id               # Delete comment
POST   /api/v1/comments/:id/like          # Like comment
```

### Favorites
```
GET    /api/v1/favorites                  # User's watchlist
POST   /api/v1/favorites                  # Add to watchlist
DELETE /api/v1/favorites/:id              # Remove from watchlist
```

### Notifications
```
GET    /api/v1/notifications              # Get user notifications
PUT    /api/v1/notifications/:id/read     # Mark as read
PUT    /api/v1/notifications/read-all     # Mark all as read
```

### Liquidity
```
GET    /api/v1/liquidity/providers        # LP leaderboard
POST   /api/v1/liquidity/add              # Record LP addition
POST   /api/v1/liquidity/withdraw         # Record LP withdrawal
GET    /api/v1/liquidity/user/:address    # User's LP positions
```

### Activity
```
GET    /api/v1/activity/feed              # Global activity feed
GET    /api/v1/activity/user/:address     # User activity
GET    /api/v1/activity/market/:id        # Market activity
```

### Analytics
```
GET    /api/v1/analytics/overview         # Platform stats
GET    /api/v1/analytics/markets/top      # Top markets
GET    /api/v1/analytics/markets/trending # Trending markets
GET    /api/v1/analytics/categories       # Category breakdown
```

## 🎯 Benefits of Web2.5 Approach

### For Users
✅ **Instant loading** - No blockchain queries
✅ **Rich profiles** - Usernames, avatars, bios
✅ **Social features** - Comments, follows, notifications
✅ **Search & filter** - Fast, powerful queries
✅ **Real-time updates** - Activity feeds, notifications
✅ **Better UX** - Feels like a normal web app

### For Developers
✅ **Easier to build** - Standard REST APIs
✅ **Better performance** - Database is fast
✅ **More features** - Can add anything
✅ **Simpler frontend** - No complex blockchain queries
✅ **Caching built-in** - Everything is cached

### Security & Trust
✅ **Blockchain validates** - All transactions on-chain
✅ **Immutable history** - Transaction records permanent
✅ **User owns assets** - Wallet controls everything
✅ **Verifiable** - Can always check blockchain
✅ **No custody** - Backend never holds funds

## 🔐 What's On-Chain vs Off-Chain

### On Sui Blockchain (Source of Truth)
- Market creation transactions
- Prediction/trade transactions
- Liquidity add/remove transactions
- Market resolution transactions
- Share balances and ownership
- **Purpose: Settlement, trust, immutability**

### In Database (Performance Layer)
- Everything above (mirrored/cached)
- Plus: Comments, favorites, notifications
- Plus: User profiles and preferences
- Plus: Analytics and aggregations
- Plus: Activity feeds and social
- **Purpose: Speed, search, social features**

## 🚀 Result

Users get a **fast, feature-rich web app** that feels like traditional platforms (Robinhood, Twitter, etc.) while maintaining all the benefits of decentralization and blockchain security.

**Best of both worlds!** 🎉

