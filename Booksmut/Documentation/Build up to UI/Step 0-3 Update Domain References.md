# Step 0-3: Update Domain References After Vercel Setup

**Purpose:** Now that Vercel has assigned your app a real domain (`reelforge-seven.vercel.app`),
you need to register that domain in two places so that R2 file access and Google sign-in work
correctly when the app is built.

**Time:** ~5 minutes

---

## Part A: Update Cloudflare R2 CORS Policy

CORS (Cross-Origin Resource Sharing) is a browser security rule. It controls which websites
are allowed to request files from your R2 bucket. Right now it's set to allow any Vercel app
(`*.vercel.app`). You're tightening it to your specific domain only.

1. Go to `https://dash.cloudflare.com`
2. Click **R2** in the left sidebar
3. Click your bucket name (`booksmut-videos` or whatever you named it)
4. Click the **Settings** tab
5. Scroll down to **CORS Policy**
6. Click **Edit**
7. Replace the existing config with this:

```json
[
  {
    "AllowedOrigins": [
      "https://reelforge-seven.vercel.app",
      "http://localhost:3000"
    ],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

8. Click **Save**

> `localhost:3000` is included so you can test locally during development without
> hitting CORS errors in your browser.

---

## Part B: Update Google Cloud OAuth Consent Screen

The OAuth consent screen controls which websites are allowed to use Google sign-in
through your Google Cloud project. When your app uses Google login (for the partner's
Gmail draft feature), Google checks that the request is coming from an authorised domain.

1. Go to `https://console.cloud.google.com`
2. Make sure you're in the correct project (check the project name in the top bar)
3. In the left sidebar, click **APIs & Services** → **OAuth consent screen**
4. Scroll down to the **Authorized domains** section
5. Click **Add domain**
6. Enter: `reelforge-seven.vercel.app`
7. Click **Save and continue** (you may need to click through a few screens — just
   keep clicking Save and continue until it confirms)

> **Note:** You do not need to add `localhost` here — Google automatically allows
> localhost for OAuth during development.

---

## What's Next

Both registrations are now done. Your Vercel domain is authorised to:
- Request files from your R2 bucket
- Use Google sign-in via your Google Cloud project

**Step 0-4:** AWS Account Setup (Lambda + SQS + SES)
