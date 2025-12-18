# DooDrop - Pet Care Tracking Web App 🐾

A playful, feature-rich web application for tracking pet care activities with role-based access control. Built with Flask and SQLAlchemy.

## Features

✨ **Core Features:**
- User authentication with role-based access (Owner, Caretaker, Admin)
- Create and manage multiple pets (dogs, cats, birds, fish, horses, and other small animals)
- Log activities: walks (with duration), meals, bathroom breaks, and custom activities
- Invite caretakers to help manage pets
- Rich activity history with timestamps and notes
- Responsive, beautifully designed interface

🎨 **Design:**
- Playful, pet-friendly branding with fun colors (yellow, coral, teal)
- Mobile-responsive design
- Smooth animations and interactions
- Emoji-enhanced interface

## Tech Stack

- **Backend:** Flask 3.0, SQLAlchemy ORM
- **Authentication:** Flask-Login with password hashing (Werkzeug)
- **Database:** SQLite (dev), PostgreSQL (recommended for production)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Deployment:** Fly.io or Netlify

## Local Setup

### Prerequisites
- Python 3.8+
- pip or poetry

### Installation

1. **Clone or download the project**
```bash
cd doodrop
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

5. **Initialize the database**
```bash
python -c "from doodrop_app import app, db; app.app_context().push(); db.create_all()"
```

6. **Run the development server**
```bash
python doodrop_app.py
```

The app will be available at `http://localhost:5000`

### Default Test Users (Development)

Create test users by registering through the sign-up page:
- **Owner:** Can add pets, invite caretakers, log activities
- **Caretaker:** Can log activities and view assigned pets
- **Admin:** Can manage all pets and users

## File Structure

```
doodrop/
├── doodrop_app.py          # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration
├── fly.toml               # Fly.io configuration
├── .env.example           # Environment variables template
└── templates/
    ├── base.html          # Base template with header/footer
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── dashboard.html     # Main dashboard
    ├── pets.html          # Pets list page
    ├── pet_detail.html    # Pet detail page with activities
    ├── pet_form.html      # Create/edit pet form
    ├── activity_form.html # Log/edit activity form
    └── add_caretaker.html # Add caretaker to pet
```

## Database Models

### User
- Email (unique)
- Username (unique)
- Password (hashed)
- Role: owner, caretaker, or admin

### Pet
- Name
- Species (dog, cat, bird, horse, fish, other)
- Breed
- Age
- Owner
- Notes

### Activity
- Type (walk, meal, bathroom, other)
- Timestamp
- Duration (for walks)
- Notes
- Associated pet and user

### Caretaker
- User
- Pet
- Added date

## API Endpoints

### Authentication
- `GET/POST /register` - Register new account
- `GET/POST /login` - Login
- `GET /logout` - Logout

### Pets
- `GET /dashboard` - Main dashboard
- `GET /pets` - List all accessible pets
- `GET/POST /pets/new` - Create new pet
- `GET /pets/<id>` - View pet details
- `GET/POST /pets/<id>/edit` - Edit pet
- `POST /pets/<id>/delete` - Delete pet
- `GET /api/pets` - Get all pets as JSON

### Activities
- `GET/POST /pets/<id>/activities/new` - Log new activity
- `GET/POST /activities/<id>/edit` - Edit activity
- `POST /activities/<id>/delete` - Delete activity
- `GET /api/pets/<id>/activities` - Get pet activities as JSON

### Caretakers
- `GET/POST /pets/<id>/caretakers/add` - Add caretaker
- `POST /pets/<id>/caretakers/<id>/remove` - Remove caretaker

## Deployment

### Fly.io (Recommended)

1. **Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Create Fly app**
```bash
flyctl launch
```

3. **Set environment variables**
```bash
flyctl secrets set SECRET_KEY="your-secret-key-here"
flyctl secrets set DATABASE_URL="postgresql://..." # if using PostgreSQL
```

4. **Deploy**
```bash
flyctl deploy
```

### Netlify

Netlify is better for static sites. For a Flask backend, you'll need:
- Use Netlify Functions (serverless) or
- Deploy Flask to another service (Fly.io, Render, Heroku) and connect from Netlify

**Recommended:** Use Fly.io for the Flask backend + Netlify for a separate frontend, or use Fly.io for both.

### Production Database Setup

For production, use PostgreSQL:

1. **On Fly.io:**
```bash
flyctl postgres create
flyctl postgres attach doodrop
```

2. **Environment variable is automatically set**

## Configuration

### Environment Variables

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@host:5432/doodrop
```

### Security Notes

- ✅ Password hashing with Werkzeug
- ✅ Session-based authentication with Flask-Login
- ✅ Role-based access control
- ✅ CSRF protection ready (use Flask-WTF if forms submitted via API)
- ⚠️ **TODO:** Add HTTPS enforcement, rate limiting, and input validation

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use a strong, random `SECRET_KEY` (min 32 characters)
- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Enable HTTPS
- [ ] Set up proper error logging
- [ ] Configure backups for database
- [ ] Review and update CORS settings if needed
- [ ] Add rate limiting for auth endpoints
- [ ] Implement proper email verification

## Development

### Running Tests (TODO)
```bash
pytest tests/
```

### Database Migrations (TODO)
Use Flask-Migrate for schema changes:
```bash
pip install Flask-Migrate
flask db init
flask db migrate
flask db upgrade
```

## Troubleshooting

### "No database found"
Run: `python -c "from doodrop_app import app, db; app.app_context().push(); db.create_all()"`

### "CSRF token missing"
Add to your form: `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>`

### Port already in use
Change port: `python doodrop_app.py --port 5001`

## Future Features

- 📸 Pet photos
- 📊 Activity analytics and insights
- 🔔 Reminders and notifications
- 📱 Mobile app
- 🌙 Dark mode
- 🇮🇳 Multi-language support
- 🏥 Veterinary appointment tracking
- 💊 Medication reminders
- 📦 Food/supply inventory

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use for personal or commercial projects

## Support

For issues, questions, or feedback, please open a GitHub issue or reach out to the team.

---

**Made with ❤️ for pet lovers everywhere. Keeping pet parents sane and parks clean! 🐕💩🐈**