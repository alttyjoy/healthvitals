# Auth Testing Playbook

## Test Identity Tracking
- Google OAuth via Emergent Auth
- JWT email/password auth (existing)

## Step 1: Create Test User & Session
```bash
mongosh --eval "
use('vitaltrack');
var sessionToken = 'test_session_' + Date.now();
db.google_sessions.insertOne({
  user_id: 'EXISTING_USER_OBJECT_ID',
  session_token: sessionToken,
  expires_at: new Date(Date.now() + 7*24*60*60*1000),
  created_at: new Date()
});
print('Session token: ' + sessionToken);
"
```

## Step 2: Test Backend API
```bash
curl -X GET "$API_URL/api/auth/me" -H "Authorization: Bearer SESSION_TOKEN"
```

## Step 3: Browser Testing
```javascript
await page.context.add_cookies([{
    name: "session_token",
    value: "YOUR_SESSION_TOKEN",
    domain: "your-app.com",
    path: "/",
    httpOnly: true,
    secure: true,
    sameSite: "None"
}]);
await page.goto("https://your-app.com");
```

## Checklist
- User document links google_id when signing in with Google
- Session token stored in httpOnly cookie
- /api/auth/me works with both JWT cookie and session_token cookie
- Google login creates new user if email not found
- Google login links to existing user if email matches
- Callback detection uses useLocation().hash
