# Step 0-2: Cloudflare R2 Bucket Setup

**Purpose:** Store generated videos and audio files with zero egress fees. Vercel frontend will download from here.

**Free Tier:** 10GB storage, 0 egress fees, unlimited reads

**Time:** ~10 minutes

---

## Part A: Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Enter your email and create a password
3. Verify your email
4. Complete the CAPTCHA
5. You're in — no credit card required for free tier

---

## Part B: Create R2 Bucket

1. Log into https://dash.cloudflare.com
2. Click **R2** in the left sidebar
3. Click **Create bucket**
4. Enter bucket name: `booksmut-videos` (must be globally unique — if taken, try `booksmut-videos-<yourname>`)
5. Select region: Choose the closest to you (e.g., `Western Europe (London)`, `US East (Florida)`)
6. Click **Create bucket**

---

## Part C: Create API Token for R2 Access

1. Click your account name (top-left) → **My Profile**
2. Click **API Tokens** tab
3. Click **Create Token**
4. Under **Custom Token**, click **Get started**
5. Token name: `booksmut-r2-upload`
6. Permissions:
   - **Account** → `Workers R2 Storage Edit` → Select your account
7. Click **Continue to summary**
8. Click **Create Token**
9. **Copy the token immediately** — you cannot see it again after closing this screen
10. Save it somewhere secure (password manager or temp `.env` file — never commit to git)

---

## Part D: Create Service User for Vercel (Optional but Recommended)

For production, create a dedicated service user instead of using your personal token:

1. Go to **R2** in Cloudflare dashboard
2. Click **Settings** → **API Access**
3. Click **Create service user**
4. Name: `booksmut-vercel`
5. Permissions: `Object Read/Write` on `booksmut-videos` bucket only
6. Click **Create**
7. Copy the **Account ID** and **Access Key ID** and **Secret Access Key**
8. Save these securely

---

## Part E: Configure CORS for Vercel Frontend

R2 buckets are private by default. You need CORS to allow your Vercel app to generate signed URLs:

1. Go to **R2** → Click your bucket name (`booksmut-videos`)
2. Click **Settings** tab
3. Scroll to **CORS policy**
4. Click **Edit**
5. Paste this CORS config:

```json
[
  {
    "AllowedOrigins": ["https://*.vercel.app"],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

6. Click **Save**

> **Note:** Replace `*.vercel.app` with your actual Vercel domain once deployed (e.g., `booksmut.vercel.app`). For local development, add `http://localhost:3000`.

---

## Part F: Set Signed URL Expiry (24 hours minimum)

Signed URLs let your frontend download videos without exposing the bucket. The expiry must be long enough that links don't die between generation and the partner clicking download.

1. Still in **R2** → **Settings**
2. Look for **Signed URL expiry** or **URL expiration** setting
3. Set to at least `86400` seconds (24 hours)
4. Click **Save**

If you don't see this setting in the UI, you'll configure it in code when generating URLs (the AWS SDK `getSignedUrl` call accepts an `expiresIn` parameter).

---

## Part G: Record Your Credentials

You will need these for your `.env` file and Vercel environment variables:

| Variable | Value | Where to Find It |
|----------|-------|------------------|
| `CLOUDFLARE_ACCOUNT_ID` | 32-character hex string | R2 dashboard URL or Settings → API Access |
| `CLOUDFLARE_R2_BUCKET_NAME` | `booksmut-videos` | You chose this in Part B |
| `CLOUDFLARE_R2_ACCESS_KEY_ID` | Starts with `r2-access-...` | Part D service user |
| `CLOUDFLARE_R2_SECRET_ACCESS_KEY` | Long random string | Part D service user |
| `R2_SIGNED_URL_EXPIRY_SECONDS` | `86400` (24 hours) | Part F or code default |

---

## Part H: Test the Bucket (Optional but Recommended)

Install the Wrangler CLI to test R2 locally:

```bash
npm install -g wrangler
wrangler login
wrangler r2 bucket list
```

Or test with a simple PUT request using curl:

```bash
curl -X PUT "https://<ACCOUNT_ID>.r2.cloudflarestorage.com/<BUCKET_NAME>/test.txt" \
  -H "Authorization: AWS <ACCESS_KEY_ID>:<SIGNATURE>" \
  -d "test content"
```

If you get a `200 OK` response, the bucket is working.

---

## What's Next

**Step 0-3:** AWS Account Setup (Lambda + SQS + SES)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bucket name already taken | Add your name or a unique suffix (e.g., `booksmut-videos-ben`) |
| CORS error in browser | Double-check `AllowedOrigins` includes your Vercel domain |
| 403 Forbidden on PUT | Verify API token has `R2 Storage Write` permission |
| Signed URL expires too fast | Increase `expiresIn` parameter in your `getSignedUrl` call |

---

## Security Notes

- **Never commit R2 credentials to git** — use `.env` locally and Vercel environment variables in production
- **Rotate tokens quarterly** — create new ones and delete old service users
- **Principle of least privilege** — service user should only access the `booksmut-videos` bucket, not all R2
