# Step 0-5: Google Cloud Service Account Setup

**Purpose:** A service account is a special Google account that your app uses to call
Google APIs automatically — without requiring a human to log in each time. Think of it
as a robot user with a specific set of permissions.

You're creating one service account that covers all four Google APIs this project uses:
Text-to-Speech, Vision, Books, and Gmail.

**Time:** ~10 minutes

---

## Part A: Open the Right Google Cloud Project

All your Google APIs must live in the same project. Make sure you're in the correct one.

1. Go to `https://console.cloud.google.com`
2. In the top bar, click the project dropdown (next to the Google Cloud logo)
3. Select the project you created when enabling the APIs (TTS, Vision, Books, Gmail)
4. Confirm the project name shows in the top bar before continuing

---

## Part B: Create the Service Account

1. In the search bar at the top, type **Service Accounts** and click it
   (full name: "Service Accounts" under IAM & Admin)
2. Click **+ Create Service Account**
3. Fill in:
   - **Service account name:** `reelforge-api-runner`
   - **Service account ID:** auto-fills as `reelforge-api-runner` — leave it
   - **Description:** `Service account for ReelForge pipeline API calls`
4. Click **Create and continue**

---

## Part C: Assign Permissions

On the **Grant this service account access to project** screen:

1. Click the **Role** dropdown
2. Search for and select each of these roles — you'll need to add them one at a time
   by clicking **+ Add another role** after each one:

   | Role Name | What It Allows |
   |-----------|---------------|
   | `Cloud Text-to-Speech API User` | Generate voiceover audio |
   | `Cloud Vision API User` | Scan video frames and cover images |
   | `Service Usage Consumer` | General API usage (required for Books API) |

3. Click **Continue**
4. On the **Grant users access** screen — leave everything blank
5. Click **Done**

> **Gmail note:** Gmail access is handled separately via OAuth (the partner signs in
> with their own Google account). The service account does not need Gmail permissions.

---

## Part D: Create and Download the Key File

The key file is a JSON file that proves to Google who your app is. Your Lambda functions
will use this file to authenticate API calls.

1. You should now see your new service account in the list — click on it
2. Click the **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON**
5. Click **Create**
6. A JSON file downloads automatically to your computer
7. **Rename it** to `reelforge-google-credentials.json`
8. Move it somewhere safe — **do not put it inside your GitHub repo folder**

> **This file is highly sensitive.** Anyone with this file can use your Google APIs
> and potentially run up charges on your account. Treat it like a password.
> Suggested location: `C:\Users\benja\OneDrive\Documents\KeePass\` or similar secure folder.

---

## Part E: Add to .gitignore

Make sure this file can never accidentally be committed to GitHub.

1. Open your repo in VS Code (`E:\Builds - Copy\Booksmut`)
2. Open the `.gitignore` file
3. Add this line if it's not already there:

```
*credentials*.json
```

4. Save the file

---

## Part F: Note the Service Account Email

Every service account has an email address — your Lambda functions will reference this
when making API calls.

1. Go back to **Service Accounts** in Google Cloud Console
2. Find `reelforge-api-runner`
3. Copy the email — it looks like:
   `reelforge-api-runner@your-project-id.iam.gserviceaccount.com`
4. Save it with your other project credentials

---

## Part G: Record Your Credentials

| Detail | Where to Find It |
|--------|-----------------|
| **Key file path** | Where you saved `reelforge-google-credentials.json` |
| **Service account email** | Part F above |
| **Google Cloud Project ID** | Top bar of Google Cloud Console — shown next to project name |

---

## What's Next

Your app can now call Google Text-to-Speech, Vision, and Books APIs automatically
using this service account.

**Step 0-6:** Hardcover.app Account + Music Library Seed
