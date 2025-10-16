# 🔗 Frontend Integration Guide

This guide explains how to integrate the Seti backend API with the React frontend.

## Environment Configuration

### Backend (.env)
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///seti.db
SUI_NETWORK=devnet
SUI_RPC_URL=https://fullnode.devnet.sui.io:443
SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
CORS_ORIGINS=http://localhost:5173
PORT=5000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api/v1
VITE_SUI_PACKAGE_ID=0x9fb4dbbd21acb0e9c3f61a6f7bf91a098ebd772f87e764fcdfe582069936fdcb
VITE_NETWORK=devnet
VITE_SUI_RPC_URL=https://fullnode.devnet.sui.io:443
```

## API Service Setup

Create an API service in your frontend:

### `src/services/api.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Markets API
export const marketsApi = {
  getAll: (params?: any) => apiClient.get('/markets', { params }),
  getById: (id: string) => apiClient.get(`/markets/${id}`),
  getFeatured: () => apiClient.get('/markets/featured'),
  getCategories: () => apiClient.get('/markets/categories'),
  sync: () => apiClient.post('/markets/sync'),
};

// Predictions API
export const predictionsApi = {
  getAll: (params?: any) => apiClient.get('/predictions', { params }),
  getById: (id: number) => apiClient.get(`/predictions/${id}`),
  create: (data: any) => apiClient.post('/predictions', data),
  getRecent: (limit?: number) => apiClient.get('/predictions/recent', { params: { limit } }),
};

// Users API
export const usersApi = {
  getProfile: (address: string) => apiClient.get(`/users/${address}`),
  updateProfile: (address: string, data: any) => apiClient.put(`/users/${address}`, data),
  getPredictions: (address: string, params?: any) => 
    apiClient.get(`/users/${address}/predictions`, { params }),
  getStats: (address: string) => apiClient.get(`/users/${address}/stats`),
  getLeaderboard: (params?: any) => apiClient.get('/users/leaderboard', { params }),
};

// Analytics API
export const analyticsApi = {
  getOverview: () => apiClient.get('/analytics/overview'),
  getTopMarkets: (metric?: string, limit?: number) => 
    apiClient.get('/analytics/markets/top', { params: { metric, limit } }),
  getCategoryStats: () => apiClient.get('/analytics/categories/stats'),
  getRecentActivity: (limit?: number) => 
    apiClient.get('/analytics/activity/recent', { params: { limit } }),
};

export default apiClient;
```

## React Query Hooks

### `src/hooks/useBackendMarkets.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { marketsApi } from '../services/api';

export function useBackendMarkets(filters?: any) {
  return useQuery({
    queryKey: ['markets', filters],
    queryFn: () => marketsApi.getAll(filters).then(res => res.data),
    staleTime: 30000, // 30 seconds
  });
}

export function useBackendMarket(marketId: string) {
  return useQuery({
    queryKey: ['market', marketId],
    queryFn: () => marketsApi.getById(marketId).then(res => res.data.market),
    enabled: !!marketId,
  });
}

export function useFeaturedMarkets() {
  return useQuery({
    queryKey: ['markets', 'featured'],
    queryFn: () => marketsApi.getFeatured().then(res => res.data.markets),
    staleTime: 60000, // 1 minute
  });
}
```

### `src/hooks/useBackendUser.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../services/api';

export function useUserProfile(address?: string) {
  return useQuery({
    queryKey: ['user', address],
    queryFn: () => usersApi.getProfile(address!).then(res => res.data.user),
    enabled: !!address,
  });
}

export function useUpdateUserProfile() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ address, data }: { address: string; data: any }) =>
      usersApi.updateProfile(address, data),
    onSuccess: (_, { address }) => {
      queryClient.invalidateQueries({ queryKey: ['user', address] });
    },
  });
}

export function useUserStats(address?: string) {
  return useQuery({
    queryKey: ['user-stats', address],
    queryFn: () => usersApi.getStats(address!).then(res => res.data.stats),
    enabled: !!address,
  });
}
```

### `src/hooks/useAnalytics.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../services/api';

export function usePlatformOverview() {
  return useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => analyticsApi.getOverview().then(res => res.data.overview),
    staleTime: 300000, // 5 minutes
  });
}

export function useTopMarkets(metric: string = 'volume', limit: number = 10) {
  return useQuery({
    queryKey: ['analytics', 'top-markets', metric, limit],
    queryFn: () => analyticsApi.getTopMarkets(metric, limit).then(res => res.data.markets),
    staleTime: 300000,
  });
}
```

## Syncing Blockchain Data

When a user makes a prediction on the blockchain, sync it to the backend:

```typescript
import { predictionsApi } from '../services/api';

// After successful blockchain transaction
async function syncPredictionToBackend(txData: any) {
  try {
    await predictionsApi.create({
      transaction_hash: txData.digest,
      market_id: txData.market_id,
      user_address: txData.user_address,
      outcome: txData.outcome,
      amount: txData.amount,
      price: txData.price,
      shares: txData.shares,
      timestamp: Math.floor(Date.now() / 1000),
    });
  } catch (error) {
    console.error('Failed to sync prediction to backend:', error);
  }
}
```

## Hybrid Data Strategy

Use both blockchain and backend data:

```typescript
// Use blockchain for authoritative data
const { data: onChainMarket } = useMarket(marketId);

// Use backend for additional analytics
const { data: backendMarket } = useBackendMarket(marketId);

// Combine data
const market = {
  ...onChainMarket,
  ...backendMarket,
  // Backend provides additional fields like prediction_count, user_activity, etc.
};
```

## Example Component

```typescript
import { useFeaturedMarkets } from '../hooks/useBackendMarkets';
import { MarketCard } from '../components/MarketCard';

function FeaturedMarkets() {
  const { data: markets, isLoading, error } = useFeaturedMarkets();
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading markets</div>;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {markets?.map(market => (
        <MarketCard key={market.id} market={market} />
      ))}
    </div>
  );
}
```

## Data Flow

1. **User creates market on blockchain**
   - Frontend calls smart contract
   - Transaction confirmed
   - Frontend calls `/api/v1/markets/sync` to index new market

2. **User places prediction**
   - Frontend calls smart contract
   - Transaction confirmed
   - Frontend calls `/api/v1/predictions` to record prediction

3. **User views dashboard**
   - Frontend fetches from backend API
   - Backend returns aggregated stats from database
   - Much faster than querying blockchain directly

## Benefits of Using Backend

1. **Performance**: Cached data, faster queries
2. **Analytics**: Complex aggregations and statistics
3. **Search**: Full-text search across markets
4. **Pagination**: Efficient pagination of large datasets
5. **Filtering**: Advanced filtering and sorting
6. **User Profiles**: Track user activity across markets

## Best Practices

1. **Use blockchain for authoritative data** (balances, ownership, etc.)
2. **Use backend for analytics and discovery** (stats, search, recommendations)
3. **Sync blockchain events to backend** for historical tracking
4. **Cache aggressively** on both frontend and backend
5. **Handle sync delays** gracefully (eventual consistency)

## Running Both Services

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd seti
npm run dev
```

Both services should now be running and communicating:
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

## Troubleshooting

### CORS Issues
Ensure `CORS_ORIGINS` in backend `.env` matches your frontend URL.

### Connection Refused
Check that backend is running on the correct port.

### Stale Data
Backend caches responses. Clear cache or wait for TTL expiration.

---

For more details, see:
- [Backend README](./README.md)
- [Frontend README](../seti/README.md)

