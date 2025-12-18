"""
DooDrop - Pet Care Tracking Web App
A Flask application for managing pet care with multiple user roles
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'doodrop-secret-dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///doodrop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@doodrop.app')

# Initialize extensions
db = SQLAlchemy(app)

# Auto-initialize database on startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Database init error: {e}")
        
        
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize SendGrid client
sg = SendGridAPIClient(SENDGRID_API_KEY) if SENDGRID_API_KEY else None

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(UserMixin, db.Model):
    """User model with role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(20), default='owner', nullable=False)  # owner, caretaker, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_pets = db.relationship('Pet', backref='owner', lazy=True, foreign_keys='Pet.owner_id')
    activities = db.relationship('Activity', backref='user', lazy=True)
    caretaker_assignments = db.relationship('Caretaker', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        # Use pbkdf2 for better Python 3.9 compatibility (scrypt needs special OpenSSL setup)
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def get_all_pets(self):
        """Get all pets user has access to (owned or caring for)"""
        if self.role == 'admin':
            return Pet.query.all()
        
        owned = Pet.query.filter_by(owner_id=self.id).all()
        caring_for = [c.pet for c in self.caretaker_assignments]
        return owned + caring_for


class Pet(db.Model):
    """Pet model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)  # dog, cat, fish, bird, other, horse
    breed = db.Column(db.String(100))
    age = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    activities = db.relationship('Activity', backref='pet', lazy=True, cascade='all, delete-orphan')
    caretakers = db.relationship('Caretaker', backref='pet', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'age': self.age,
            'owner_id': self.owner_id,
            'notes': self.notes
        }


class Activity(db.Model):
    """Activity tracking model"""
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # walk, meal, bathroom, other
    timestamp = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # duration in minutes (for walks)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'user_name': User.query.get(self.user_id).username
        }


class Caretaker(db.Model):
    """Caretaker assignment model - supports both existing users and email invitations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for pending invites
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)  # Email for invitations or existing user
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    
    __table_args__ = (db.UniqueConstraint('email', 'pet_id', name='_caretaker_email_pet_uc'),)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        user_name = User.query.get(self.user_id).username if self.user_id else 'Pending'
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pet_id': self.pet_id,
            'email': self.email,
            'status': self.status,
            'user_name': user_name,
            'invited_at': self.invited_at.isoformat()
        }


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    return User.query.get(int(user_id))


# ============================================================================
# EMAIL UTILITIES
# ============================================================================

def send_email(to_email, subject, html_content):
    """Send email via SendGrid"""
    if not sg:
        print(f"⚠️  Email not configured. Would send to {to_email}: {subject}")
        return False
    
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        response = sg.send(message)
        print(f"✅ Email sent to {to_email} (status: {response.status_code})")
        return response.status_code in [200, 201, 202]
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def send_caretaker_invitation_email(caretaker_email, pet_name, owner_name, app_url="http://localhost:8000"):
    """Send caretaker invitation email"""
    subject = f"You're invited to help care for {pet_name} on DooDrop! 🐾"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #FFB804 0%, #FE8262 100%); padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">🐾 DooDrop Caretaker Invitation</h1>
                </div>
                
                <p>Hi there!</p>
                
                <p><strong>{owner_name}</strong> has invited you to help care for <strong>{pet_name}</strong> on DooDrop!</p>
                
                <div style="background: #f5eded; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>What's DooDrop?</strong></p>
                    <p>DooDrop is a pet care tracking app that helps pet owners and their helpers stay on the same page with:</p>
                    <ul>
                        <li>📝 Activity logging (walks, meals, bathroom breaks)</li>
                        <li>👥 Shared access for family and pet sitters</li>
                        <li>📊 Pet care history and insights</li>
                    </ul>
                </div>
                
                <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #479AAC;">
                    <p style="margin: 0; font-weight: bold;">Next steps:</p>
                    <ol>
                        <li>Click the link below to join DooDrop</li>
                        <li>Sign up with this email address: <strong>{caretaker_email}</strong></li>
                        <li>You'll automatically gain access to {pet_name}!</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{app_url}/register" style="display: inline-block; background: #FFB804; color: white; padding: 12px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px;">
                        Join DooDrop 🚀
                    </a>
                </div>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    For the giggles, wiggles, and those little... squiggles! 🐕💩🐈<br>
                    © 2024 DooDrop. Keeping pet parents sane and parks clean.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(caretaker_email, subject, html_content)


# ============================================================================
# DECORATORS
# ============================================================================

def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def owner_or_caretaker(pet_id):
    """Check if current user is owner or accepted caretaker of pet"""
    pet = Pet.query.get(pet_id)
    if not pet:
        return False
    
    if pet.owner_id == current_user.id:
        return True
    
    # Check for accepted caretaker assignment
    caretaker = Caretaker.query.filter_by(
        email=current_user.email,
        pet_id=pet_id,
        status='accepted'  # Only accepted caretakers can access
    ).first()
    
    return caretaker is not None


# ============================================================================
# ROUTES - AUTH
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'owner')
        
        # Validate
        if not email or not username or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        if role not in ['owner', 'caretaker', 'admin']:
            role = 'owner'
        
        # Create user
        user = User(email=email, username=username, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            return redirect(next_page)
        
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))


# ============================================================================
# ROUTES - MAIN
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    pets = current_user.get_all_pets()
    return render_template('dashboard.html', pets=pets)


@app.route('/pets')
@login_required
def pets_list():
    """List all pets user has access to"""
    pets = current_user.get_all_pets()
    return render_template('pets.html', pets=pets)


@app.route('/pets/new', methods=['GET', 'POST'])
@login_required
@require_role('owner', 'admin')
def new_pet():
    """Create new pet"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        species = data.get('species', '').strip()
        breed = data.get('breed', '').strip()
        age = data.get('age')
        notes = data.get('notes', '').strip()
        
        if not name or not species:
            return jsonify({'error': 'Name and species are required'}), 400
        
        pet = Pet(
            name=name,
            species=species,
            breed=breed,
            age=int(age) if age else None,
            owner_id=current_user.id,
            notes=notes
        )
        
        db.session.add(pet)
        db.session.commit()
        
        return redirect(url_for('pet_detail', pet_id=pet.id))
    
    species_list = ['dog', 'cat', 'freshwater fish', 'bird', 'horse', 'other small animal']
    return render_template('pet_form.html', species_list=species_list)


@app.route('/pets/<int:pet_id>')
@login_required
def pet_detail(pet_id):
    """Pet detail page"""
    pet = Pet.query.get_or_404(pet_id)
    
    if not owner_or_caretaker(pet_id):
        return redirect(url_for('dashboard'))
    
    # Get recent activities
    activities = Activity.query.filter_by(pet_id=pet_id).order_by(
        Activity.timestamp.desc()
    ).limit(20).all()
    
    caretakers = Caretaker.query.filter_by(pet_id=pet_id).all()
    
    return render_template('pet_detail.html', pet=pet, activities=activities, caretakers=caretakers)


@app.route('/pets/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    """Edit pet"""
    pet = Pet.query.get_or_404(pet_id)
    
    if pet.owner_id != current_user.id and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        pet.name = data.get('name', pet.name).strip()
        pet.species = data.get('species', pet.species).strip()
        pet.breed = data.get('breed', pet.breed).strip()
        pet.age = int(data.get('age')) if data.get('age') else pet.age
        pet.notes = data.get('notes', pet.notes).strip()
        
        db.session.commit()
        
        return redirect(url_for('pet_detail', pet_id=pet.id))
    
    species_list = ['dog', 'cat', 'freshwater fish', 'bird', 'horse', 'other small animal']
    return render_template('pet_form.html', pet=pet, species_list=species_list, edit=True)


@app.route('/pets/<int:pet_id>/delete', methods=['POST'])
@login_required
@require_role('owner', 'admin')
def delete_pet(pet_id):
    """Delete pet"""
    pet = Pet.query.get_or_404(pet_id)
    
    if pet.owner_id != current_user.id and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    db.session.delete(pet)
    db.session.commit()
    
    return redirect(url_for('pets_list'))


# ============================================================================
# ROUTES - CARETAKERS
# ============================================================================

@app.route('/pets/<int:pet_id>/caretakers/add', methods=['GET', 'POST'])
@login_required
@require_role('owner', 'admin')
def add_caretaker(pet_id):
    """Add caretaker to pet"""
    pet = Pet.query.get_or_404(pet_id)
    
    if pet.owner_id != current_user.id and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        caretaker_email = data.get('caretaker_email', '').strip().lower()
        
        if not caretaker_email:
            if request.is_json:
                return jsonify({'error': 'Email is required'}), 400
            return render_template('add_caretaker.html', pet=pet, error='Email is required')
        
        # Check if email already a caretaker for this pet
        existing = Caretaker.query.filter_by(
            email=caretaker_email,
            pet_id=pet_id
        ).first()
        
        if existing:
            if existing.status == 'pending':
                error_msg = f'Invitation already sent to {caretaker_email}'
            else:
                error_msg = f'{caretaker_email} is already a caretaker for {pet.name}'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            return render_template('add_caretaker.html', pet=pet, error=error_msg)
        
        # Check if email is the owner
        if caretaker_email == current_user.email:
            error_msg = 'Cannot add the pet owner as a caretaker'
            if request.is_json:
                return jsonify({'error': error_msg}), 400
            return render_template('add_caretaker.html', pet=pet, error=error_msg)
        
        # Look up if user exists with this email
        user = User.query.filter_by(email=caretaker_email).first()
        
        # Create caretaker invitation (works whether user exists or not)
        caretaker_assignment = Caretaker(
            user_id=user.id if user else None,
            pet_id=pet_id,
            email=caretaker_email,
            status='accepted' if user else 'pending'  # Auto-accept if user exists
        )
        
        if user:
            caretaker_assignment.accepted_at = datetime.utcnow()
        
        db.session.add(caretaker_assignment)
        db.session.commit()
        
        # Send invitation email
        if not user:
            # New invitation - send welcome email
            send_caretaker_invitation_email(
                caretaker_email, 
                pet.name, 
                current_user.username,
                app_url=request.host_url.rstrip('/')
            )
        else:
            # Existing user - could send notification here if desired
            pass
        
        success_msg = f'Invitation sent to {caretaker_email}' if not user else f'{user.username} added as caretaker'
        
        if request.is_json:
            return jsonify({'success': True, 'message': success_msg}), 201
        
        return redirect(url_for('pet_detail', pet_id=pet_id))
    
    return render_template('add_caretaker.html', pet=pet)


@app.route('/pets/<int:pet_id>/caretakers/<int:caretaker_id>/remove', methods=['POST'])
@login_required
@require_role('owner', 'admin')
def remove_caretaker(pet_id, caretaker_id):
    """Remove caretaker from pet"""
    pet = Pet.query.get_or_404(pet_id)
    
    if pet.owner_id != current_user.id and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    caretaker = Caretaker.query.get_or_404(caretaker_id)
    
    if caretaker.pet_id != pet_id:
        return redirect(url_for('pet_detail', pet_id=pet_id))
    
    db.session.delete(caretaker)
    db.session.commit()
    
    return redirect(url_for('pet_detail', pet_id=pet_id))


# ============================================================================
# ROUTES - ACTIVITIES
# ============================================================================

@app.route('/pets/<int:pet_id>/activities/new', methods=['GET', 'POST'])
@login_required
def new_activity(pet_id):
    """Log new activity"""
    pet = Pet.query.get_or_404(pet_id)
    
    if not owner_or_caretaker(pet_id):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        activity_type = data.get('activity_type', '').strip()
        timestamp_str = data.get('timestamp', '')
        duration = data.get('duration')
        notes = data.get('notes', '').strip()
        
        if not activity_type:
            return jsonify({'error': 'Activity type is required'}), 400
        
        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
        
        activity = Activity(
            pet_id=pet_id,
            user_id=current_user.id,
            activity_type=activity_type,
            timestamp=timestamp,
            duration=int(duration) if duration and activity_type == 'walk' else None,
            notes=notes
        )
        
        db.session.add(activity)
        db.session.commit()
        
        if request.is_json:
            return jsonify(activity.to_dict()), 201
        
        return redirect(url_for('pet_detail', pet_id=pet_id))
    
    activity_types = ['walk', 'meal', 'bathroom', 'other']
    return render_template('activity_form.html', pet=pet, activity_types=activity_types)


@app.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):
    """Edit activity"""
    activity = Activity.query.get_or_404(activity_id)
    
    if activity.user_id != current_user.id and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    pet = activity.pet
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        activity.activity_type = data.get('activity_type', activity.activity_type).strip()
        
        timestamp_str = data.get('timestamp')
        if timestamp_str:
            try:
                activity.timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                pass
        
        if activity.activity_type == 'walk' and data.get('duration'):
            activity.duration = int(data.get('duration'))
        else:
            activity.duration = None
        
        activity.notes = data.get('notes', activity.notes).strip()
        
        db.session.commit()
        
        if request.is_json:
            return jsonify(activity.to_dict())
        
        return redirect(url_for('pet_detail', pet_id=pet.id))
    
    activity_types = ['walk', 'meal', 'bathroom', 'other']
    return render_template('activity_form.html', pet=pet, activity=activity, activity_types=activity_types, edit=True)


@app.route('/activities/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    """Delete activity"""
    activity = Activity.query.get_or_404(activity_id)
    
    if activity.user_id != current_user.id and current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    pet_id = activity.pet_id
    
    db.session.delete(activity)
    db.session.commit()
    
    return redirect(url_for('pet_detail', pet_id=pet_id))


# ============================================================================
# ROUTES - API (for AJAX requests)
# ============================================================================

@app.route('/api/pets/<int:pet_id>/activities', methods=['GET'])
@login_required
def get_pet_activities(pet_id):
    """Get activities for a pet (API)"""
    if not owner_or_caretaker(pet_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    activities = Activity.query.filter_by(pet_id=pet_id).order_by(
        Activity.timestamp.desc()
    ).all()
    
    return jsonify([a.to_dict() for a in activities])


@app.route('/api/pets', methods=['GET'])
@login_required
def get_user_pets():
    """Get all pets for current user (API)"""
    pets = current_user.get_all_pets()
    return jsonify([p.to_dict() for p in pets])


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(403)
def forbidden(error):
    """403 error handler"""
    return render_template('error.html', error='Access denied'), 403


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    print(f"❌ 500 Error: {error}")
    import traceback
    traceback.print_exc()
    return render_template('error.html', error='Internal server error. Check the logs for details.'), 500
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            import traceback
            traceback.print_exc()
    
    # Get port from environment or use 8000 for local dev
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🐾 DooDrop starting on http://0.0.0.0:{port}")
    
    # Listen on 0.0.0.0 for production (Fly.io, etc.)
    app.run(host='0.0.0.0', port=port, debug=debug)