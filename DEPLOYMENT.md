# DooDrop Deployment Guide 🚀

## Quick Comparison

| Platform | Best For | Setup Time | Cost |
|----------|----------|-----------|------|
| **Fly.io** | Full-stack Flask apps | ~15 min | Free tier + pay-as-you-go |
| **Netlify** | Frontend only | N/A | Free tier available |
| **Heroku** | Full-stack (classic) | ~10 min | Paid (removed free tier) |
| **Render** | Full-stack Flask apps | ~15 min | Free tier + pay-as-you-go |

**Recommendation: Use Fly.io** - It's perfect for Flask apps with a generous free tier and easy scaling.

---

## Option 1: Deploy to Fly.io (Recommended) ⭐

### Prerequisites
- Fly.io account (free at https://fly.io)
- Fly CLI installed
- Git (optional, but recommended)

### Step-by-Step

#### 1. Install Fly CLI

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```bash
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

#### 2. Login to Fly.io
```bash
flyctl auth login
```

#### 3. Prepare Your App

Make sure you have all files in the correct structure:
```
doodrop/
├── doodrop_app.py
├── requirements.txt
├── Procfile
├── fly.toml
├── .env.example
├── README.md
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── pets.html
    ├── pet_detail.html
    ├── pet_form.html
    ├── activity_form.html
    ├── add_caretaker.html
    └── error.html
```

#### 4. Create Fly App
```bash
cd doodrop
flyctl launch --name doodrop
```

When prompted:
- **Dockerfile:** Choose "Generate a Dockerfile"
- **PostgreSQL:** Say "yes" (or you can set it up later)
- **Deploy now:** Say "no" (we'll deploy after config)

#### 5. Configure Secrets
```bash
# Generate a random secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set it in Fly
flyctl secrets set SECRET_KEY="<paste-the-generated-key>"
```

If you created a PostgreSQL database in step 4, Fly automatically sets `DATABASE_URL`.

If not, set it manually:
```bash
flyctl secrets set DATABASE_URL="postgresql://user:password@host:5432/doodrop"
```

Or for SQLite (simpler but less scalable):
```bash
flyctl secrets set DATABASE_URL="sqlite:///doodrop.db"
```

#### 6. Deploy
```bash
flyctl deploy
```

#### 7. Get Your App URL
```bash
flyctl apps info
```

Visit the URL and you should see DooDrop! 🎉

#### 8. Check Logs (if something goes wrong)
```bash
flyctl logs
```

### Scaling & Monitoring

**View app status:**
```bash
flyctl status
```

**Scale replicas (load balancing):**
```bash
flyctl scale count 2
```

**Monitor metrics:**
```bash
flyctl metrics
```

**Connect to database (if PostgreSQL):**
```bash
flyctl postgres connect -a doodrop-db
```

### Updating Your App

1. Make changes locally
2. Commit to git (optional but recommended)
3. Deploy:
```bash
flyctl deploy
```

### Custom Domain

```bash
flyctl certs create yourdomain.com
# Follow DNS setup instructions
```

---

## Option 2: Deploy to Netlify + Render

If you prefer to split frontend and backend:

### Backend on Render.com

1. Go to https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repo (or upload manually)
4. Set start command: `gunicorn doodrop_app:app`
5. Add environment variables (SECRET_KEY, DATABASE_URL)
6. Deploy

### Frontend on Netlify

1. Go to https://netlify.com
2. Create a simple HTML dashboard that points to your Render backend API
3. Use environment variables to configure API endpoint

**Note:** This is more complex. Stick with Fly.io for simplicity.

---

## Option 3: Deploy to Heroku (Legacy, Requires Credit Card)

Heroku removed its free tier in 2022, so you'll need a credit card, but it's still easy:

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create doodrop

# Create PostgreSQL database
heroku addons:create heroku-postgresql:hobby-dev

# Set secret
heroku config:set SECRET_KEY="<your-secret-key>"

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

---

## Database Setup

### Using SQLite (Development Only)
```bash
# In Fly, set:
flyctl secrets set DATABASE_URL="sqlite:///doodrop.db"

# ⚠️ Note: Fly uses ephemeral storage, so SQLite data will be lost on restarts!
# Only use for testing.
```

### Using PostgreSQL (Recommended)

#### On Fly.io (Easiest)
```bash
flyctl postgres create
flyctl postgres attach doodrop
# DATABASE_URL is set automatically
```

#### On External Provider (AWS RDS, Azure Database, etc.)
```bash
# Get connection string and set it:
flyctl secrets set DATABASE_URL="postgresql://user:pass@host:5432/doodrop"
```

#### Connection String Format
```
postgresql://username:password@host:port/database_name

# Example:
postgresql://admin:mypassword123@db.example.com:5432/doodrop
```

---

## Environment Variables Checklist

Make sure these are set in your platform:

```
FLASK_ENV=production
SECRET_KEY=<min-32-random-characters>
DATABASE_URL=<your-database-url>
```

### Generating a Secure Secret Key

```python
# Python
import secrets
print(secrets.token_hex(32))

# Or bash
openssl rand -hex 32
```

---

## Monitoring & Debugging

### Check Logs
**Fly.io:**
```bash
flyctl logs -a doodrop
```

**Heroku:**
```bash
heroku logs --tail -a doodrop
```

**Render:**
```bash
# View in dashboard at render.com
```

### Common Issues

#### "Database connection error"
- Verify `DATABASE_URL` is set correctly
- Check if database is running
- Ensure database has correct permissions

#### "Static files not found"
- Flask serves files from `static/` folder (create if missing)
- Add to `doodrop_app.py`:
```python
from flask import Flask
app = Flask(__name__, static_folder='static', static_url_path='/static')
```

#### "Port already in use"
- Fly.io and others set `PORT` environment variable
- Update `doodrop_app.py`:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

#### "Timeout errors"
- Database queries taking too long
- Add indexing to frequently queried columns
- Implement pagination for large result sets

---

## Security in Production

✅ **Checklist:**
- [ ] Set `FLASK_ENV=production`
- [ ] Use strong, random `SECRET_KEY` (min 32 chars)
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS (automatic on Fly.io)
- [ ] Set secure cookies: `SESSION_COOKIE_SECURE=True`
- [ ] Add CORS headers if needed
- [ ] Enable CSRF protection
- [ ] Use environment variables for secrets (not in code)
- [ ] Implement rate limiting for auth endpoints
- [ ] Add input validation and sanitization
- [ ] Enable database backups
- [ ] Set up error alerting/monitoring

### Enhanced Security Setup

Add to `doodrop_app.py`:
```python
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 3600  # 1 week
```

---

## Backup Strategy

### Fly.io + PostgreSQL
```bash
# Automated backups are included

# Manual backup:
flyctl postgres backup create

# List backups:
flyctl postgres backups list -a doodrop-db

# Restore:
flyctl postgres restore -a doodrop-db
```

### External Database
- Enable automated backups in your database provider
- Test restore process monthly
- Store backups in separate region

---

## Performance Optimization

### Database Optimization
```python
# Add database indexes for common queries
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    name = db.Column(db.String(100), index=True)

class Activity(db.Model):
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), index=True)
    timestamp = db.Column(db.DateTime, index=True)
```

### Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/pets')
@cache.cached(timeout=300)
def get_pets():
    # This will be cached for 5 minutes
    return jsonify([p.to_dict() for p in Pet.query.all()])
```

### Connection Pooling (for PostgreSQL)
```python
from sqlalchemy.pool import QueuePool

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': QueuePool,
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

---

## Rollback & Recovery

If something breaks after deployment:

**Fly.io:**
```bash
# View deployment history
flyctl releases

# Rollback to previous version
flyctl releases rollback
```

**Heroku:**
```bash
# View releases
heroku releases -a doodrop

# Rollback
heroku releases:rollback v10 -a doodrop
```

---

## CI/CD (Continuous Deployment)

### GitHub Actions (Fly.io)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Fly

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Then set `FLY_API_TOKEN` in GitHub repo secrets:
```bash
flyctl auth token
```

---

## Questions?

- **Fly.io Docs:** https://fly.io/docs/
- **Flask Docs:** https://flask.palletsprojects.com/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Deployment Help:** Create an issue in your repo

Good luck deploying! 🚀🐾