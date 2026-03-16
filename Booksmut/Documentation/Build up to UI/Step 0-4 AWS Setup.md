# Step 0-4: AWS Account Setup

**Purpose:** AWS runs three things for this project:
- **Lambda** — executes the video processing and pipeline code
- **SQS** — queues jobs between pipeline stages so nothing gets lost
- **SES** — sends you alert emails when something fails

**Free Tier:** 400,000 GB-seconds Lambda/month, 1M SQS requests/month, 62K SES emails/month
— all well within what this project needs at MVP.

**Time:** ~20 minutes

---

## Part A: Create AWS Account

If you already have an AWS account, skip to Part B.

1. Go to `https://aws.amazon.com` → click **Create an AWS Account**
2. Enter your email and choose an account name (e.g. `reelforge`)
3. Select **Personal** account type
4. Enter payment details — required by AWS even for free tier. You will not be charged
   if you stay within free tier limits
5. Verify your phone number
6. Select the **Free** support plan
7. Sign in to the AWS Console

---

## Part B: Set Your Default Region

All services must be in the same region or they can't talk to each other efficiently.

1. Log into `https://console.aws.amazon.com`
2. In the top-right corner, click the region dropdown (shows something like `US East (N. Virginia)`)
3. Select the region closest to you:
   - UK/Europe → **EU (London) — eu-west-2**
   - US East → **US East (N. Virginia) — us-east-1**
   - US West → **US West (Oregon) — us-west-2**
4. **Remember this region** — you will need to select it every time you return to the console

> Every service you create in Parts C, D, and E must be in this same region.

---

## Part C: Create the Lambda Execution Role (IAM)

IAM (Identity and Access Management) controls what your Lambda functions are allowed to do.
You're creating a role — a set of permissions — that all Lambda functions in this project
will use.

1. In the AWS Console search bar, type **IAM** and click it
2. Click **Roles** in the left sidebar
3. Click **Create role**
4. Under **Trusted entity type**, select **AWS service**
5. Under **Use case**, select **Lambda**
6. Click **Next**
7. On the **Add permissions** screen, search for and tick each of these policies:
   - `AmazonSQSFullAccess`
   - `AmazonSESFullAccess`
   - `CloudWatchLogsFullAccess` (so Lambda logs appear in CloudWatch)
8. Click **Next**
9. Role name: `reelforge-lambda-role`
10. Click **Create role**

> **What this does:** Every Lambda function you create later will be assigned this role.
> It gives Lambda permission to send messages to SQS queues, send emails via SES,
> and write logs so you can see what happened.

---

## Part D: Verify SQS is Available

SQS (Simple Queue Service) is already available in your account — no setup needed beyond
confirming it's there.

1. In the AWS Console search bar, type **SQS** and click it
2. You should see the SQS dashboard with a **Create queue** button
3. You don't need to create any queues yet — that happens in Phase 2
4. Just confirm the page loads without errors

---

## Part E: Set Up SES (Email Alerts)

SES (Simple Email Service) sends you alert emails when the pipeline fails. By default,
new AWS accounts start in "sandbox mode" — you can only send emails to addresses you
have manually verified.

**Verify your email address:**

1. In the AWS Console search bar, type **SES** and click it
2. In the left sidebar, click **Verified identities**
3. Click **Create identity**
4. Select **Email address**
5. Enter your email address
6. Click **Create identity**
7. Check your inbox — AWS sends a verification email
8. Click the verification link in that email
9. Return to SES → Verified identities — your email should now show **Verified**

> This is the address that will receive pipeline failure alerts. Use an email you
> actually check regularly.

**Note on sandbox mode:** In sandbox mode you can only send TO verified addresses.
This is fine for the project — you're only emailing yourself with alerts.
If you ever want to email users, you'd need to request production access, but
that's not needed here.

---

## Part F: Record Your AWS Details

You will need these later when configuring Lambda functions and environment variables:

| Detail | Where to Find It |
|--------|-----------------|
| **AWS Account ID** | Click your account name (top-right) → it shows a 12-digit number |
| **Default Region** | The region you selected in Part B (e.g. `eu-west-2`) |
| **Lambda Role ARN** | IAM → Roles → `reelforge-lambda-role` → copy the ARN at the top |
| **Verified SES Email** | The email you verified in Part E |

An ARN looks like: `arn:aws:iam::123456789012:role/reelforge-lambda-role`

Save these somewhere accessible — you'll need them in Phase 2 when building the pipeline.

---

## What's Next

AWS is now configured with:
- A Lambda execution role with the right permissions
- SQS available and ready for queue creation in Phase 2
- SES verified and ready to send alert emails

**Step 0-5:** Hardcover.app Account + Music Library Seed
