# Mock Authentication Walkthrough

We have implemented a **Hybrid Mock Authentication** system that allows you to simulate different user roles (Admin, Primary, Secondary, Guest) while interacting with the real database logic.

## 1. How to Enable Mock Auth
Ensure your `.env` file in `backend/` has the following line:
```bash
USE_MOCK_AUTH=true
```
And your `frontend/.env` (or `frontend/.env.local`) has:
```bash
VITE_USE_MOCK_AUTH=true
```

## 2. Using the Toolbar
1.  Navigate to `http://localhost:5173`.
2.  Look for the **"Mock Auth"** toolbar in the bottom-left corner.
3.  Click the arrow (▲) to expand it.

### Switching Users
-   Select a **User Group** from the dropdown (e.g., "Primary Users").
-   Click on any user in the list (e.g., "Primary 1").
-   The page will reload, and you will be logged in as that user.

### Verification
-   **Dashboard**: You should see "Welcome, Primary 1" (or similar name).
-   **Admin**: Login as "Mock Admin" to access admin-only pages (once implemented).

## 3. Persistent Sessions
The mock session is stored in your browser's LocalStorage. It will persist across reloads until you click **Logout** in the Mock Auth toolbar.

## Screens
![Mock Auth Toolbar Expanded](/home/ghirschhorn/.gemini/antigravity/brain/0167bf5c-ba59-463f-ba7c-a6a6fbe23d91/mock_auth_expanded_1770513779638.png)
