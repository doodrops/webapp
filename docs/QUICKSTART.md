# DooDrop Quick Start Guide 🚀

Get DooDrop running in 5 minutes!

## What You're Getting

A complete Flask web app for pet care tracking with:
- ✅ User authentication (3 roles: owner, caretaker, admin)
- ✅ Pet management (6 species types)
- ✅ Activity logging (walks, meals, bathroom breaks, custom)
- ✅ Caretaker management (invite others to help)
- ✅ Beautiful responsive UI (matches your Doodrop brand)
- ✅ Ready to deploy to Fly.io or Netlify

## Files Included

```
doodrop/
├── doodrop_app.py           # Main Flask application (599 lines)
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment config
├── fly.toml                 # Fly.io config
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # Full documentation
├── DEPLOYMENT.md            # Detailed deployment guide
└── templates/               # HTML templates (11 files)
    ├── base.html           # Base template with header/footer
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── dashboard.html      # Main dashboard
    ├── pets.html           # Pets list
    ├── pet_detail.html     # Pet profile with activities
    ├── pet_form.html       # Create/edit pet
    ├── activity_form.html  # Log activity
    ├── add_caretaker.html  # Invite caretaker
    └── error.html          # Error page
```

## 5-Minute Local Setup

### 1. Install Python 3.8+
- macOS: `brew install python3`
- Windows: Download from python.org
- Linux: `sudo apt install python3 python3-pip`

### 2. Extract Files
Unzip the downloaded files into a folder called `doodrop`

### 3. Create Virtual Environment
```bash
cd doodrop
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
python doodrop_app.py
```

Open your browser to `http://localhost:5000`

### 6. Create a Test Account
Click "Sign Up" and register with:
- **Role:** Owner (to create pets)
- **Username:** testuser
- **Email:** test@example.com
- **Password:** anything

### 7. Try It Out
1. Add a pet 🐕
2. Log an activity 📝
3. Invite a caretaker 👥

## Key Features to Demo

### Owner Features
- ✅ Create/edit/delete pets
- ✅ Invite caretakers
- ✅ Log activities
- ✅ Remove caretakers

### Caretaker Features
- ✅ View assigned pets
- ✅ Log activities
- ✅ Update pet info
- ❌ Cannot delete pets

### Admin Features
- ✅ Full access to all pets and users
- ✅ Manage everything

## Database

The app uses **SQLite** by default (file-based, no setup needed).

Database file: `doodrop.db` (created automatically)

To reset: Delete `doodrop.db` and restart the app

## Customize It

### Change Brand Colors
Open `templates/base.html` and edit the `:root` CSS variables:
```css
:root {
    --primary: #FFB804;    /* Yellow */
    --coral: #FE8262;      /* Coral */
    --teal: #479AAC;       /* Teal */
    --dark: #1a1410;       /* Dark */
    --gray: #5a524c;       /* Gray */
    --light: #f5eded;      /* Light */
    --cream: #ede6e1;      /* Cream */
}
```

### Add More Pet Species
Edit `doodrop_app.py` line ~325:
```python
species_list = ['dog', 'cat', 'freshwater fish', 'bird', 'horse', 'other small animal', 'YOUR_SPECIES']
```

### Add Activity Types
Edit the same file, add to the activity types list:
```python
activity_types = ['walk', 'meal', 'bathroom', 'other', 'YOUR_ACTIVITY']
```

### Change App Name
1. Search `DooDrop` in templates
2. Search `doodrop` in app files
3. Replace with your brand name

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Address already in use"
```bash
# Use a different port
python doodrop_app.py --port 5001
```

### "Database locked"
```bash
# Delete the database and restart
rm doodrop.db
python doodrop_app.py
```

### Can't create account
- Email must be unique
- Username must be unique
- All fields required

## Ready to Deploy?

### Fly.io (Recommended - Easiest)

1. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/
2. Login: `flyctl auth login`
3. Deploy:
   ```bash
   flyctl launch --name doodrop
   flyctl secrets set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   flyctl deploy
   ```
4. Visit the URL shown in terminal ✨

**Cost:** Free tier available, then ~$5-10/month for small app

### Netlify

Netlify is for static sites only. For Flask, you need a backend service.

**Options:**
1. Deploy Flask to Fly.io, connect from Netlify frontend
2. Use Netlify Functions (serverless) - more complex setup

**Recommendation:** Use Fly.io for the whole app

## Next Steps

1. **Read DEPLOYMENT.md** for detailed deploy instructions
2. **Read README.md** for API documentation
3. **Customize templates** to match your exact design
4. **Add features** like photo uploads, reminders, analytics
5. **Deploy** to Fly.io or your preferred platform

## File Descriptions

| File | Purpose | Edit? |
|------|---------|-------|
| `doodrop_app.py` | Main app logic | Yes (for customization) |
| `templates/*.html` | UI pages | Yes (for styling) |
| `requirements.txt` | Dependencies | No (unless adding packages) |
| `fly.toml` | Fly.io config | For advanced users |
| `.env.example` | Environment template | Copy to `.env` locally |

## Common Customizations

### 1. Change Pet Species
File: `doodrop_app.py`, function `new_pet()`
```python
species_list = ['dog', 'cat', 'bird', 'fish', 'hamster']
```

### 2. Add Fields to Pet Profile
File: `doodrop_app.py`, class `Pet`
```python
class Pet(db.Model):
    # Add new field
    microchip = db.Column(db.String(100))
```

### 3. Customize Colors
File: `templates/base.html`, `:root` section

### 4. Add Logo
File: `templates/base.html`
```html
<img src="/static/logo.png" style="width: 40px;">
```

## API Endpoints Reference

```
GET  /                      # Home (redirects to dashboard)
GET  /dashboard             # Main dashboard
GET  /login                 # Login form
POST /login                 # Submit login
GET  /register              # Registration form
POST /register              # Submit registration
GET  /logout                # Logout
GET  /pets                  # List all pets
GET  /pets/new              # New pet form
POST /pets/new              # Create pet
GET  /pets/<id>             # Pet details
GET  /pets/<id>/edit        # Edit pet form
POST /pets/<id>/edit        # Save pet
POST /pets/<id>/delete      # Delete pet
GET  /pets/<id>/activities/new      # Log activity form
POST /pets/<id>/activities/new      # Log activity
GET  /activities/<id>/edit          # Edit activity form
POST /activities/<id>/edit          # Save activity
POST /activities/<id>/delete        # Delete activity
GET  /pets/<id>/caretakers/add      # Add caretaker form
POST /pets/<id>/caretakers/add      # Invite caretaker
POST /pets/<id>/caretakers/<id>/remove  # Remove caretaker
GET  /api/pets              # All pets (JSON)
GET  /api/pets/<id>/activities  # Pet activities (JSON)
```

## Questions?

- **Setup issues:** Check DEPLOYMENT.md
- **Feature requests:** Edit files per customization guide
- **Design changes:** Modify templates/*.html
- **Database questions:** See SQLAlchemy docs

## You're All Set! 🎉

Your Doodrop pet care app is ready to:
- ✅ Run locally
- ✅ Be customized
- ✅ Be deployed
- ✅ Scale to production

Start with step 5 above to see it in action, then deploy when ready!

Questions? Check the README.md for comprehensive documentation.

Happy tracking! 🐾