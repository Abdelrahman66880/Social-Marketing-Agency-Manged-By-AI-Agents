# Frontend-Backend Integration Guide

This guide explains how the frontend fully integrates with the FastAPI backend for the Social Marketing Agency platform.

## Quick Start

### 1. Ensure Backend is Running

```bash
# In the src/ directory
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
# Backend should be running on http://localhost:8000
```

### 2. Start Frontend

```bash
# In the frontend/ directory
npm install
npm run dev
# Frontend should be running on http://localhost:3000
```

### 3. Test Integration

1. Open http://localhost:3000
2. You should see login page
3. Try registering a new account
4. Login should redirect to dashboard

## API Endpoint Mapping

### Authentication Routes

**Backend**: `src/routes/auth.py`

| Frontend Action | Backend Endpoint | Method | Purpose |
|---|---|---|---|
| Register page submit | `POST /auth/register` | POST | Create new user account |
| Login page submit | `POST /auth/token` | POST | Get JWT access token |
| Auto-login after register | `POST /auth/token` | POST | Login with credentials |

**Request/Response Examples**:

```typescript
// Register
POST /auth/register
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
Response: { "signal": "USER_REGISTERED_SUCCESSFULLY" }

// Login
POST /auth/token (form-data)
username=john@example.com&password=securepass123
Response: {
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Content/Drafts Routes

**Backend**: `src/routes/drafts.py`

| Frontend Page | Endpoint | Method | Purpose |
|---|---|---|---|
| Content page | `GET /drafts/users/{userId}/{limit}/{skip}` | GET | List draft posts |
| Content page | `POST /drafts` | POST | Create new draft |
| Content page | `PUT /drafts/{draftId}` | PUT | Edit draft content |
| Content page | `PUT /drafts/{draftId}/accept` | PUT | Approve draft |
| Content page | `PUT /drafts/{draftId}/reject` | PUT | Reject draft |

**Implementation in Frontend**:

```typescript
// In hooks/useAPI.ts useDrafts() hook
const fetchDrafts = useCallback(async () => {
  const data = await api.drafts.getDraftsByUser(userId);
  setDrafts(data);
}, [userId]);

const createDraft = useCallback(async (title: string, content: string) => {
  const draft = await api.drafts.createDraft({
    title,
    content,
    user_id: userId,
  });
  addDraft(draft);
}, [userId]);
```

**Request/Response Example**:

```typescript
// Create draft
POST /drafts
{
  "title": "Best AI Practices",
  "content": "Artificial Intelligence is transforming businesses...",
  "user_id": "66fe9e7fbd12f8f9c9f3e3d2"
}

Response: {
  "id": "66fe9e7fbd12f8f9c9f3e3a1",
  "title": "Best AI Practices",
  "content": "...",
  "status": "draft",
  "user_id": "66fe9e7fbd12f8f9c9f3e3d2",
  "createdAt": "2025-10-05T14:00:00Z"
}
```

### Schedule Routes

**Backend**: `src/routes/schedule.py`

| Frontend Page | Endpoint | Method | Purpose |
|---|---|---|---|
| Schedule page | `GET /schedule/users/{userId}` | GET | Get user schedule |
| Schedule page | `PUT /schedule/users/{userId}` | PUT | Update schedule |

**Implementation**:

```typescript
// In hooks/useAPI.ts useSchedule() hook
const fetchSchedule = useCallback(async () => {
  const data = await api.schedule.getSchedule(userId);
  setSchedule(data);
}, [userId]);

const updateSchedule = useCallback(async (newSchedule: Schedule) => {
  const updated = await api.schedule.editSchedule(userId, newSchedule);
  setSchedule(updated);
}, [userId]);
```

**Data Structure**:

```typescript
// Schedule format
{
  "id": "66fe9e7fbd12f8f9c9f3e3a1",
  "user_id": "66fe9e7fbd12f8f9c9f3e3d2",
  "posts": [
    {
      "id": "post_1",
      "date": "2025-10-10T09:00:00Z",
      "content": "Generate an AI post about sustainable tech",
      "media_urls": []
    }
  ],
  "competitor_analysis": [],
  "interaction_analysis_dates": []
}
```

### Facebook Integration Routes

**Backend**: `src/routes/facebook.py`

| Frontend Action | Endpoint | Method | Purpose |
|---|---|---|---|
| Settings page | `POST /facebook/pages/{pageId}/post?page_access_token=...` | POST | Upload post to Facebook |
| Settings page | `GET /facebook/pages/{pageId}/info?page_access_token=...` | GET | Get page info |

**Implementation**:

```typescript
// In hooks/useAPI.ts useFacebookIntegration()
const uploadPost = useCallback(
  async (pageId: string, accessToken: string, message: string, imageUrl?: string) => {
    return await api.facebook.uploadPost(pageId, accessToken, {
      message,
      image_url: imageUrl || null,
      video_url: null,
    });
  },
  []
);
```

## Data Flow Examples

### Example 1: Create and Approve a Draft

```
1. User types content in Content page
   ↓
2. Clicks "Create Draft" button
   ↓
3. Frontend calls: api.drafts.createDraft({title, content, user_id})
   ↓
4. Backend: POST /drafts
   - Validates input (title 3-100 chars, content 100+ chars)
   - Stores in MongoDB with status="DRAFT"
   - Returns Post object with ID
   ↓
5. Frontend stores draft in Zustand state (useAppStore)
   ↓
6. Displays in drafts list
   ↓
7. User clicks "Approve" button
   ↓
8. Frontend calls: api.drafts.approveDraft(draftId)
   ↓
9. Backend: PUT /drafts/{draftId}/accept
   - Updates status to "ACCEPTED"
   - Returns confirmation
   ↓
10. Frontend updates local state
    ↓
11. Draft moves to "Accepted" section
```

### Example 2: Login and Session Management

```
1. User visits http://localhost:3000
   ↓
2. useProtectedRoute() checks localStorage for "access_token"
   ↓
3. If no token, redirects to /login
   ↓
4. User enters email/password
   ↓
5. Frontend calls: api.auth.login(email, password)
   ↓
6. Sends: POST /auth/token (form-data: username=email, password=password)
   ↓
7. Backend validates against MongoDB users collection
   - Checks bcrypt hashed password
   - Verifies accountStatus is ACTIVE
   ↓
8. Backend returns: {access_token: "jwt_token", token_type: "bearer"}
   ↓
9. Frontend stores token: localStorage.setItem("access_token", token)
   ↓
10. useAuthStore updates: setIsAuthenticated(true)
    ↓
11. Redirects to /dashboard
    ↓
12. All subsequent API calls include: Authorization: Bearer {token}
```

### Example 3: Schedule Management

```
1. User navigates to /schedule
   ↓
2. useSchedule(userId) hook triggers fetchSchedule()
   ↓
3. Frontend calls: api.schedule.getSchedule(userId)
   ↓
4. Backend: GET /schedule/users/{userId}
   - Queries MongoDB for schedule matching user_id
   - Returns Schedule object with posts array
   ↓
5. Frontend updates: setSchedule(data)
   ↓
6. User fills in date/time and content
   ↓
7. Clicks "Schedule" button
   ↓
8. Frontend updates local schedule object:
   schedule.posts.push({
     date: newPostDate,
     content: newPostContent,
     media_urls: []
   })
   ↓
9. Calls: api.schedule.editSchedule(userId, updatedSchedule)
   ↓
10. Backend: PUT /schedule/users/{userId}
    - Updates MongoDB schedule document
    - Returns updated Schedule
    ↓
11. Frontend updates state
    ↓
12. Post appears in scheduled list
```

## Error Handling Flow

### When API Returns Error

```
try {
  const result = await api.drafts.createDraft(data)
} catch (err: any) {
  // Frontend catches error
  const errorMsg = err?.detail?.message || err?.detail || "Failed"
  setError(errorMsg)
  
  // Displays in Alert component
  <Alert variant="destructive">
    <AlertDescription>{error}</AlertDescription>
  </Alert>
}
```

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "Post validation failed: content must be at least 100 characters"
}
```

**401 Unauthorized**
```json
{
  "detail": "Incorrect email or password"
}
```

**404 Not Found**
```json
{
  "detail": "Draft not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Failed to create draft for the following reason: database error"
}
```

## State Persistence

### What Gets Persisted

**localStorage**:
```javascript
// After login
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "auth-store": "{\"isAuthenticated\": true, \"user\": {\"id\": \"...\", \"username\": \"john\", ...}}"
}
```

**Zustand (useAuthStore)**:
- `isAuthenticated`
- `user` object
- Persisted via zustand/middleware

**Zustand (useAppStore)**:
- `drafts` array
- `schedule` object
- `notifications` array
- NOT persisted (resets on page refresh)

## Protected Route Authorization

### How Protection Works

```typescript
// In app/dashboard/page.tsx
const isReady = useProtectedRoute()

if (!isReady) {
  return <LoadingSpinner />
}

// Component only renders if authenticated
```

### Flow

```
1. User tries to access /dashboard
2. useProtectedRoute() checks localStorage
3. If token exists: returns true (renders component)
4. If no token: returns false, redirects to /login
```

## Token Management

### Token Injection

All API calls automatically include token:

```typescript
// In lib/api.ts
const getAuthHeader = () => {
  const token = getToken()
  if (!token) return {}
  return {
    Authorization: `Bearer ${token}`,
  }
}

// Applied to every request:
fetch(url, {
  headers: {
    "Content-Type": "application/json",
    ...getAuthHeader(), // Adds Authorization header
  }
})
```

### Token Expiration Handling

```typescript
if (!response.ok && response.status === 401) {
  removeToken()
  if (typeof window !== "undefined") {
    window.location.href = "/login"
  }
}
```

## Development Tips

### Test API Call Directly

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"testpass123"}'

# Login
curl -X POST http://localhost:8000/auth/token \
  -d "username=test@example.com&password=testpass123" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Create draft (with token)
curl -X POST http://localhost:8000/drafts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title":"My Post",
    "content":"This is a test post with more than 100 characters to meet the minimum requirement for content.",
    "user_id":"USERID"
  }'
```

### Debug API Calls

Add logging to `lib/api.ts`:

```typescript
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  console.log(`[API] ${options.method || 'GET'} ${endpoint}`)
  console.log(`[API] Request body:`, options.body)
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, ...)
  
  console.log(`[API] Response status:`, response.status)
  const data = await response.json()
  console.log(`[API] Response data:`, data)
  
  return data
}
```

### Inspect State

```typescript
// In any component
const store = useAppStore()
console.log("Current app state:", store)

const auth = useAuthStore()
console.log("Current auth state:", auth)
```

## Testing Checklist

- [ ] Register new user → verify in MongoDB
- [ ] Login with created user → verify token in localStorage
- [ ] Create draft → appears in content page
- [ ] Edit draft → content updates
- [ ] Approve draft → status changes to ACCEPTED
- [ ] Schedule post → appears in schedule page
- [ ] Remove scheduled post → removed from list
- [ ] Open chat → can send messages
- [ ] Open settings → shows user info
- [ ] Click logout → redirects to login, clears token
- [ ] Manually clear localStorage → redirects to login
- [ ] Modify token in localStorage → next API call fails (401)

## Troubleshooting Integration Issues

### Issue: "Cannot POST /auth/register"

**Cause**: Backend not running
**Solution**: Start backend with `python -m uvicorn main:app --reload`

### Issue: "CORS error: Access-Control-Allow-Origin"

**Cause**: Backend CORS not configured
**Solution**: Backend should have CORS middleware enabled

### Issue: "401 Unauthorized" on all requests

**Cause**: Token not being sent or expired
**Solution**: 
- Check localStorage has "access_token"
- Try logging out and back in
- Check backend JWT_SECRET matches

### Issue: Draft not appearing after creation

**Cause**: Frontend state not updating
**Solution**: 
- Check API returned success (no error)
- Verify draft appears in API response
- Check Zustand store is being updated

## Next Steps

1. **Replace simulated responses**:
   - Chat page currently simulates agent responses
   - Connect to backend chat endpoints when available

2. **Add real-time features**:
   - WebSocket for chat messages
   - Live notifications
   - Real-time analytics updates

3. **Implement missing features**:
   - Analytics dashboard
   - Advanced scheduling (recurring posts)
   - Image upload
   - Draft templates

4. **Performance optimization**:
   - Implement pagination
   - Add caching layer
   - Optimize re-renders

5. **Testing**:
   - Add unit tests for hooks
   - Add integration tests
   - Add E2E tests with Playwright/Cypress
