# DooDrop SendGrid Email Integration 📧

Email notifications are now integrated! Caretakers receive beautiful invitation emails when added to a pet.

## Setup (3 Steps)

### Step 1: Get Your SendGrid API Key

1. Go to https://sendgrid.com
2. Sign up (free tier available - 100 emails/day)
3. Go to Settings → API Keys
4. Create a new API key (Full Access)
5. Copy the key (save it somewhere safe)

### Step 2: Install SendGrid Package

```bash
pip install sendgrid
```

Or if already installed:
```bash
pip install -r requirements.txt
```

### Step 3: Add Environment Variables

Create or update `.env` file:

```bash
SENDGRID_API_KEY=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
SENDGRID_FROM_EMAIL=noreply@doodrop.me
```

**For local testing**, you can use:
```bash
SENDGRID_FROM_EMAIL=noreply@doodrop.me
```

## Testing

### Local Testing (Without API Key)

If you don't set `SENDGRID_API_KEY`, emails are **simulated**:
```
⚠️ Email not configured. Would send to caretaker@example.com: You're invited to help care for Buddy on DooDrop! 🐾
```

Great for testing without sending real emails!

### Production Testing (With API Key)

1. Set SENDGRID_API_KEY in `.env`
2. Restart app: `python doodrop_app.py`
3. Add a caretaker with a real email
4. Check inbox - email should arrive in seconds!

## What Gets Emailed

### Caretaker Invitation Email

Sent when owner adds someone **without an existing account**:

- ✅ Beautiful branded email with DooDrop colors
- ✅ Explains what DooDrop is
- ✅ Clear call-to-action button
- ✅ Link to join with their email pre-filled
- ✅ Pet name and owner name shown

**Subject:** "You're invited to help care for [Pet Name] on DooDrop! 🐾"

**When sent:** Immediately when owner adds them as caretaker

**Example:**
```
From: noreply@doodrop.app
To: alice@example.com
Subject: You're invited to help care for Buddy on DooDrop! 🐾

[Beautiful HTML email with invitation]
```

### No Email Sent If...

- Caretaker already has account (status: "accepted")
- Caretaker removes themselves
- Owner removes caretaker

(These could be added later if desired)

## Configuration

### Custom From Email

Default: `noreply@doodrop.app`

Change in `.env`:
```bash
SENDGRID_FROM_EMAIL=hello@mycompany.com
```

**Requirements:**
- Must be verified in SendGrid
- For Twilio account, use verified sender domain

### Custom Email Subject/Content

Edit `send_caretaker_invitation_email()` in `doodrop_app.py`:

```python
def send_caretaker_invitation_email(caretaker_email, pet_name, owner_name, app_url="..."):
    subject = f"Custom subject here"  # Change this
    html_content = f"""Custom HTML"""  # Change this
```

## Deployment to Fly.io

### Step 1: Set Environment Variables

```bash
flyctl secrets set SENDGRID_API_KEY="SG.xxxxx..."
flyctl secrets set SENDGRID_FROM_EMAIL="noreply@yourdomain.com"
```

### Step 2: Deploy

```bash
flyctl deploy
```

That's it! Emails will work in production.

## SendGrid Free Tier

- ✅ 100 emails/day
- ✅ Unlimited contacts
- ✅ Email tracking
- ✅ A/B testing
- ✅ Template builder

Paid plans start at $14.95/month for unlimited emails.

## Troubleshooting

### "SENDGRID_API_KEY not set"

Solution: Set the environment variable
```bash
export SENDGRID_API_KEY="SG.xxxx"
python doodrop_app.py
```

### "Invalid API key"

Check that:
1. Key is correct (copy-pasted fully)
2. Key hasn't been revoked in SendGrid
3. No extra spaces/quotes around key

### "Email not sending"

Check logs for errors:
```bash
python doodrop_app.py  # Look for error messages
```

Common issues:
- `From` email not verified in SendGrid
- API key has insufficient permissions
- Invalid recipient email

### "Emails going to spam"

SendGrid has good deliverability. But check:
1. From email is verified
2. SPF/DKIM records set up
3. Unsubscribe link included (included by default)

## Email Features (Future)

### Could Add:
- 📧 Activity digest emails
- 🔔 Caretaker accepted notification
- ⏰ Pet care reminders
- 📋 Weekly activity summary
- 💬 Messages between owner and caretaker

## Code Reference

### Sending Email

```python
send_email(to_email, subject, html_content)
```

### Sending Caretaker Invitation

```python
send_caretaker_invitation_email(
    caretaker_email="alice@example.com",
    pet_name="Buddy",
    owner_name="Sarah",
    app_url="http://localhost:8000"
)
```

### Disabling Emails

Just don't set `SENDGRID_API_KEY` in environment. Email functions will silently skip.

## Files Updated

- **doodrop_app.py**
  - Added SendGrid imports and initialization
  - Added `send_email()` function
  - Added `send_caretaker_invitation_email()` function
  - Updated `add_caretaker` route to send invites

- **requirements.txt**
  - Added `sendgrid==6.11.0`

- **.env.example**
  - Added SENDGRID_API_KEY
  - Added SENDGRID_FROM_EMAIL

## Getting Started

1. Ensure SendGrid is installed: `pip install sendgrid`
2. Get API key from SendGrid
3. Set environment variables in `.env`
4. Restart app: `python doodrop_app.py`
5. Add a caretaker and watch the email appear!

Questions? Check SendGrid docs: https://sendgrid.com/docs/

Happy emailing! 📧🐾