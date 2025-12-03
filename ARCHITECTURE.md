# Project Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                         │
│                    http://localhost:3000                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    App Pages                            │   │
│  │  ┌──────────┬──────────┬──────────┬──────────────────┐  │   │
│  │  │  /login  │/register │/dashboard│ /content, etc.  │  │   │
│  │  └──────────┴──────────┴──────────┴──────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓ (API calls)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 API Client Layer                        │   │
│  │              lib/api.ts (Centralized)                  │   │
│  │  ├─ auth.register/login                               │   │
│  │  ├─ drafts.create/edit/approve                        │   │
│  │  ├─ schedule.get/update                               │   │
│  │  ├─ facebook.uploadPost                               │   │
│  │  └─ notifications.get                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────┬───────────────────────────────┐  │
│  │    State Management      │    Custom Hooks              │  │
│  │   (Zustand Stores)       │   (useAPI.ts)                │  │
│  │ ├─ useAuthStore          │ ├─ useAuth()                 │  │
│  │ └─ useAppStore           │ ├─ useDrafts()               │  │
│  │                          │ ├─ useSchedule()             │  │
│  │                          │ ├─ useFacebookIntegration()  │  │
│  │                          │ └─ useProtectedRoute()       │  │
│  └──────────────────────────┴───────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              UI Components (Shadcn)                     │   │
│  │  Card, Button, Input, Select, Badge, Alert, etc.      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          localStorage (Token Storage)                   │   │
│  │  - access_token (JWT)                                  │   │
│  │  - auth-store (Zustand persistence)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                     ↓ (HTTP Requests)
                 HTTPS/TCP IP Port 8000
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                             │
│                  http://localhost:8000                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API Routes (RouterS)                       │   │
│  │  ├─ /auth (register, login, token)                     │   │
│  │  ├─ /drafts (create, list, edit, approve, reject)     │   │
│  │  ├─ /schedule (get, create, update)                   │   │
│  │  ├─ /facebook (upload, get info, etc.)                │   │
│  │  ├─ /analytics (get, create)                          │   │
│  │  └─ /notifications (get, mark read)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Authentication & Validation                   │   │
│  │  ├─ JWT token validation                               │   │
│  │  ├─ Pydantic model validation                          │   │
│  │  ├─ Password hashing (bcrypt)                          │   │
│  │  └─ Role-based access control                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            Database Models & ORM                        │   │
│  │  ├─ models/db_schemas/                                 │   │
│  │  │  ├─ User.py (username, email, password)            │   │
│  │  │  ├─ Post.py (drafts, status, content)              │   │
│  │  │  ├─ Schedule.py (posts, analysis schedule)         │   │
│  │  │  ├─ Analysis.py (analytics data)                   │   │
│  │  │  └─ etc.                                            │   │
│  │  └─ models/*Model.py (Repository layer)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Business Logic Layer                          │   │
│  │  ├─ agents/ (AI agents)                                │   │
│  │  │  ├─ GeneratorAgent.py (content generation)         │   │
│  │  │  ├─ AnalyzerAgent.py (analytics)                   │   │
│  │  │  ├─ RecommenderAgent.py (recommendations)          │   │
│  │  │  └─ ExecutorAgent.py (execution)                   │   │
│  │  ├─ controllers/ (business logic)                      │   │
│  │  │  └─ facebook.py (Facebook API integration)         │   │
│  │  └─ stores/ (LLM services)                            │   │
│  │     └─ LLMs.py (OpenAI, HuggingFace)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         External Integrations                           │   │
│  │  ├─ MongoDB (NoSQL database)                           │   │
│  │  ├─ Facebook Graph API                                │   │
│  │  ├─ OpenAI API (ChatGPT)                              │   │
│  │  ├─ HuggingFace API                                    │   │
│  │  └─ SendGrid / Email Service                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                     ↓ (Database Queries)
┌─────────────────────────────────────────────────────────────────┐
│                  MONGODB (NoSQL Database)                       │
│                                                                 │
│  Collections:                                                   │
│  ├─ users (accounts, credentials)                              │
│  ├─ posts (drafts, published posts)                            │
│  ├─ schedules (scheduled content)                              │
│  ├─ analyses (analytics data)                                  │
│  ├─ notifications (user notifications)                         │
│  ├─ recommendations (AI recommendations)                       │
│  └─ business_info (business details)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
Social-Marketing-Agency-Manged-By-AI-Agents/
├── frontend/                           # Next.js Application
│   ├── app/                           # App Router (Pages)
│   │   ├── login/page.tsx            # Login page
│   │   ├── register/page.tsx         # Registration page
│   │   ├── dashboard/page.tsx        # Dashboard (protected)
│   │   ├── content/page.tsx          # Content generation (protected)
│   │   ├── schedule/page.tsx         # Scheduling (protected)
│   │   ├── chat/page.tsx             # AI chat (protected)
│   │   ├── settings/page.tsx         # Settings (protected)
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Home page
│   │   └── globals.css               # Global styles
│   │
│   ├── lib/
│   │   ├── api.ts                    # API client (all endpoints)
│   │   ├── types.ts                  # TypeScript interfaces
│   │   └── utils.ts                  # Utility functions
│   │
│   ├── store/
│   │   └── index.ts                  # Zustand stores (auth, app)
│   │
│   ├── hooks/
│   │   ├── useAPI.ts                 # Custom hooks (auth, drafts, etc.)
│   │   ├── use-mobile.ts             # Mobile detection
│   │   └── use-toast.ts              # Toast notifications
│   │
│   ├── components/
│   │   ├── ui/                       # Shadcn UI components
│   │   ├── navigation.tsx            # Navigation bar
│   │   ├── theme-provider.tsx        # Theme setup
│   │   └── [other components]
│   │
│   ├── public/                       # Static assets
│   ├── styles/                       # Styling
│   │
│   ├── package.json                  # Dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── next.config.mjs               # Next.js config
│   ├── tailwind.config.ts            # Tailwind config
│   ├── postcss.config.mjs            # PostCSS config
│   │
│   ├── README.md                     # Frontend documentation
│   ├── CONFIGURATION.md              # Configuration guide
│   └── .env.example                  # Environment template
│
├── src/                              # FastAPI Backend
│   ├── main.py                      # FastAPI app entry
│   │
│   ├── routes/                      # API endpoints
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── drafts.py               # Draft management
│   │   ├── schedule.py             # Schedule management
│   │   ├── facebook.py             # Facebook integration
│   │   ├── analytics.py            # Analytics
│   │   ├── notifications.py        # Notifications
│   │   └── [other routes]
│   │
│   ├── models/                     # Data models
│   │   ├── db_schemas/            # MongoDB schemas
│   │   │   ├── User.py
│   │   │   ├── Post.py
│   │   │   ├── Schedule.py
│   │   │   ├── Analysis.py
│   │   │   └── [others]
│   │   ├── enums/                 # Enumerations
│   │   ├── schemas/               # Request/Response schemas
│   │   └── *Model.py              # Repository classes
│   │
│   ├── agents/                    # AI Agents
│   │   ├── GeneratorAgent.py     # Content generation
│   │   ├── AnalyzerAgent.py      # Analysis
│   │   ├── RecommenderAgent.py   # Recommendations
│   │   └── ExecutorAgent.py      # Execution
│   │
│   ├── controllers/              # Business logic
│   │   └── facebook.py          # Facebook controller
│   │
│   ├── helpers/                 # Configuration
│   │   └── config.py           # Settings, env vars
│   │
│   ├── stores/                 # LLM services
│   │   └── LLMs.py            # AI model integrations
│   │
│   ├── tools/                 # Tools & utilities
│   │   └── tools.py          # Helper tools
│   │
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment template
│
├── docker/                    # Docker configuration
│   └── docker-compose.yml    # Docker compose setup
│
├── docs/                     # Documentation
│   └── [api docs, etc.]
│
├── INTEGRATION.md            # Frontend-Backend integration guide
└── README.md                # Project README
```

## Data Flow Examples

### User Registration & Login

```
1. Frontend: User enters credentials on /register
   ↓
2. Frontend: Calls api.auth.register()
   ↓
3. Backend: Receives POST /auth/register
   - Validates input (email format, password length)
   - Hashes password with bcrypt
   - Creates User in MongoDB
   ↓
4. Backend: Returns success signal
   ↓
5. Frontend: Auto-calls api.auth.login()
   ↓
6. Backend: Receives POST /auth/token
   - Finds user by email
   - Verifies password
   - Generates JWT token
   ↓
7. Backend: Returns { access_token, token_type }
   ↓
8. Frontend: Stores token in localStorage
   ↓
9. Frontend: Redirects to /dashboard
   ↓
10. All subsequent requests include Authorization header
```

### Creating and Scheduling Content

```
1. Frontend: User goes to /content
   ↓
2. Frontend: Calls useDrafts(userId).fetchDrafts()
   ↓
3. Backend: GET /drafts/users/{userId}/{limit}/{skip}
   - Queries MongoDB for user's draft posts
   - Returns list
   ↓
4. Frontend: Displays drafts in list
   ↓
5. Frontend: User fills in form and clicks "Create Draft"
   ↓
6. Backend: POST /drafts
   - Creates Post with status=DRAFT
   - Stores in MongoDB
   ↓
7. Frontend: Adds to drafts list in UI
   ↓
8. Frontend: User clicks "Approve"
   ↓
9. Backend: PUT /drafts/{id}/accept
   - Updates status to ACCEPTED
   ↓
10. Frontend: Moves draft to accepted section
    ↓
11. Frontend: User goes to /schedule
    ↓
12. Backend: GET /schedule/users/{userId}
    - Retrieves schedule document
    ↓
13. Frontend: Displays scheduled posts
    ↓
14. Frontend: User adds new scheduled post
    ↓
15. Backend: PUT /schedule/users/{userId}
    - Updates schedule with new post
    ↓
16. Frontend: Post appears in calendar
```

## Technology Choices

### Frontend Stack
- **Next.js 16**: React framework with SSR, API routes, optimizations
- **React 19**: Latest React with automatic batching
- **TypeScript**: Type safety and better DX
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn UI**: Pre-built components library
- **Zustand**: Lightweight state management
- **date-fns**: Date formatting and manipulation

### Backend Stack
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for flexible schemas
- **PyMongo/Motor**: Async MongoDB driver
- **Pydantic**: Data validation and serialization
- **JWT (PyJWT)**: Stateless authentication
- **bcrypt**: Password hashing
- **Python 3.10+**: Latest Python features

### External Services
- **Facebook Graph API**: Social media posting
- **OpenAI API**: LLM for content generation
- **HuggingFace**: Alternative AI models
- **SendGrid**: Email service
- **MongoDB Atlas**: Cloud database (optional)

## Authentication Flow

```
┌─────────────────────────────────────┐
│  User enters email/password         │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Frontend POST /auth/token          │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Backend validates credentials      │
│  - Finds user in MongoDB            │
│  - Checks bcrypt password hash      │
│  - Verifies account is ACTIVE       │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Backend generates JWT token        │
│  - Includes user ID in sub claim    │
│  - Sets expiration time             │
│  - Signs with JWT_SECRET            │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Frontend receives token            │
│  - Stores in localStorage           │
│  - Updates Zustand auth state       │
│  - Sets in useAuthStore             │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Frontend auto-includes in headers  │
│  Authorization: Bearer {token}      │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Backend validates token on each    │
│  request before processing          │
│  - Decodes JWT                      │
│  - Extracts user ID                 │
│  - Proceeds with authorization      │
└─────────────────────────────────────┘
```

## State Management Strategy

```
┌────────────────────────────────────────────────────┐
│         Global State (Zustand)                     │
├────────────────────────────────────────────────────┤
│                                                    │
│  useAuthStore (Persisted)                         │
│  ├─ user: User | null                             │
│  ├─ isAuthenticated: boolean                      │
│  ├─ isLoading: boolean                            │
│  ├─ error: string | null                          │
│  └─ Actions: setUser(), logout(), etc.            │
│                                                    │
│  useAppStore (Not Persisted)                      │
│  ├─ drafts: Post[]                                │
│  ├─ schedule: Schedule | null                     │
│  ├─ notifications: Notification[]                 │
│  ├─ selectedDraftId: string | null                │
│  └─ Actions: setDrafts(), addDraft(), etc.        │
│                                                    │
└────────────────────────────────────────────────────┘
                        ↑
                  Used by custom
                   hooks which
                   make API calls
                        ↑
┌────────────────────────────────────────────────────┐
│         Custom Hooks (useAPI.ts)                   │
├────────────────────────────────────────────────────┤
│                                                    │
│  useAuth()                                         │
│  - Manages login/register/logout                  │
│  - Handles auth flow                              │
│                                                    │
│  useDrafts(userId)                                │
│  - Fetches and manages draft posts                │
│  - Performs CRUD operations                       │
│                                                    │
│  useSchedule(userId)                              │
│  - Manages schedule data                          │
│  - Handles scheduling logic                       │
│                                                    │
│  useProtectedRoute()                              │
│  - Checks authentication                          │
│  - Redirects if not authorized                    │
│                                                    │
│  [More hooks...]                                  │
│                                                    │
└────────────────────────────────────────────────────┘
                        ↑
              Used by Page Components
                        ↑
┌────────────────────────────────────────────────────┐
│         Page Components                            │
├────────────────────────────────────────────────────┤
│                                                    │
│  app/dashboard/page.tsx                           │
│  app/content/page.tsx                             │
│  app/schedule/page.tsx                            │
│  app/chat/page.tsx                                │
│  app/settings/page.tsx                            │
│                                                    │
│  Each component:                                  │
│  - Uses appropriate hooks                         │
│  - Displays UI based on state                     │
│  - Triggers actions on user interaction           │
│  - Updates Zustand store                          │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Performance Considerations

1. **Code Splitting**: Each page is a separate bundle
2. **Lazy Loading**: Components can be lazy-loaded with React.lazy()
3. **Memoization**: Use React.memo() for expensive components
4. **API Caching**: Consider caching API responses
5. **Image Optimization**: Use Next.js Image component
6. **Token Refresh**: Implement refresh token rotation

## Security Measures

1. **CORS**: Frontend enforces CORS headers
2. **JWT**: Secure token-based authentication
3. **HTTPS**: Should use HTTPS in production
4. **Environment Variables**: Sensitive data in .env
5. **Input Validation**: Pydantic validates on backend
6. **Password Hashing**: bcrypt with salt
7. **Token Expiration**: Tokens expire after set time
8. **XSS Prevention**: React escapes by default

## Future Enhancements

1. **Real-time Features**:
   - WebSocket for chat
   - Server-sent events for notifications
   - Live notifications

2. **Advanced Features**:
   - Content recommendations from AI
   - Advanced analytics dashboard
   - Multi-user team collaboration
   - Draft versioning

3. **Performance**:
   - Database indexing optimization
   - Redis caching
   - CDN for static assets
   - Database query optimization

4. **Integrations**:
   - Instagram integration
   - TikTok integration
   - Twitter/X integration
   - LinkedIn integration

5. **Testing**:
   - Unit tests (Jest, Vitest)
   - Integration tests
   - E2E tests (Playwright, Cypress)
   - Performance testing
