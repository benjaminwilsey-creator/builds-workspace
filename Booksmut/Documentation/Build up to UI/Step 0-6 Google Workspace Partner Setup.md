# Step 0-6: Add Partner to Google Workspace

**Purpose:** Add your partner as a user in your Google Workspace organisation so she can
sign in to ReelForge using a managed Google account. This keeps the app on the Internal
OAuth type — no Google verification review required.

**Time:** ~5 minutes

---

## Part A: Add the User

1. Go to `https://admin.google.com`
2. Sign in with your Workspace admin account
3. Click **Directory** → **Users**
4. Click **Add new user**
5. Fill in:
   - **First name:** Partner's first name
   - **Last name:** Partner's last name
   - **Primary email:** choose something like `firstname@yourdomain.com`
6. Click **Add new user**
7. Google will show you a temporary password — copy it and send it to your partner

---

## Part B: Set Her Role

By default she'll be added as a regular user — that's correct. She does not need admin access.

If you want to limit what she can see in Google Workspace:
1. Click her name in the Users list
2. Click **Admin roles and privileges**
3. Confirm she has no admin roles assigned

---

## Part C: Have Her Sign In and Change Password

1. She goes to `https://accounts.google.com`
2. Signs in with the email you created and the temporary password
3. Google will prompt her to set a new password immediately
4. Done — she now has a managed Google account

---

## Part D: Add Her as a Test User (Until App is Live)

While the app is in development, Google requires you to explicitly list who can sign in
via OAuth — even for Internal apps.

1. Google Cloud Console → APIs & Services → OAuth consent screen
2. Scroll to **Test users**
3. Click **Add users**
4. Enter her new Workspace email address
5. Click **Save**

---

## What This Means for the App

When your partner clicks "Sign in with Google" in ReelForge, she'll use this Workspace
account. The Gmail drafts for publisher outreach will be created in her Gmail inbox
at this address — make sure she checks this inbox, not her personal email.

---

## What's Next

**Step 0-7:** Music Library Seed — source 20+ royalty-free tracks for the video pipeline
