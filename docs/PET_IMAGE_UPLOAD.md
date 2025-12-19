# DooDrop Image Upload Implementation

## Step-by-Step Changes

### 1. Create uploads folder
```bash
cd /Users/ctoddlombardo/Desktop/code/doodrops/new_app
mkdir -p static/uploads/pets
```

### 2. Update app.py - Add imports at top
Add after other imports:
```python
from werkzeug.utils import secure_filename
import os
from pathlib import Path
```

### 3. Add configuration to app
Add after `app = Flask(__name__)`:
```python
# File upload configuration
UPLOAD_FOLDER = 'static/uploads/pets'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
```

### 4. Add helper function
Add this function before the Pet class:
```python
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_pet_image(file, pet_id):
    """Save uploaded image and return filename"""
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'pet_{pet_id}.{ext}'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None
```

### 5. Update Pet model
In the `Pet` class, add this field:
```python
image_filename = db.Column(db.String(255))  # Store image filename
```

Update the `to_dict()` method to include:
```python
'image_filename': self.image_filename
```

### 6. Update add_pet route
Find the `@app.route('/pets/new', ...)` route and update it:

**OLD CODE:**
```python
@app.route('/pets/new', methods=['GET', 'POST'])
@login_required
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed')
        age = request.form.get('age', type=int)
        notes = request.form.get('notes')
        
        pet = Pet(name=name, species=species, breed=breed, age=age, notes=notes, owner_id=current_user.id)
        db.session.add(pet)
        db.session.commit()
        
        flash('Pet added successfully!', 'success')
        return redirect(url_for('pets'))
    
    species_list = ['dog', 'cat', 'fish', 'bird', 'horse', 'other']
    return render_template('pet_form.html', species_list=species_list)
```

**NEW CODE:**
```python
@app.route('/pets/new', methods=['GET', 'POST'])
@login_required
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed')
        age = request.form.get('age', type=int)
        notes = request.form.get('notes')
        
        pet = Pet(name=name, species=species, breed=breed, age=age, notes=notes, owner_id=current_user.id)
        db.session.add(pet)
        db.session.commit()
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = save_pet_image(file, pet.id)
                pet.image_filename = filename
                db.session.commit()
        
        flash('Pet added successfully!', 'success')
        return redirect(url_for('pets'))
    
    species_list = ['dog', 'cat', 'fish', 'bird', 'horse', 'other']
    return render_template('pet_form.html', species_list=species_list)
```

### 7. Update edit_pet route
Find `@app.route('/pets/<int:pet_id>/edit', ...)` and add image handling:

```python
# Handle image upload
if 'image' in request.files:
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = save_pet_image(file, pet.id)
        pet.image_filename = filename

db.session.commit()
```

### 8. Update pet_form.html template
Add this section in the "Additional Information" form-section, before the notes:

```html
<div class="form-section">
    <h3>Pet Photo</h3>
    
    {% if edit and pet.image_filename %}
    <div class="form-group">
        <p>Current photo:</p>
        <img src="/{{ pet.image_filename }}" alt="{{ pet.name }}" style="max-width: 200px; border-radius: 10px; margin-bottom: 1rem;">
        <p style="font-size: 0.9rem; color: var(--gray);">Upload a new photo to replace it</p>
    </div>
    {% endif %}
    
    <div class="form-group">
        <label for="image">Upload Pet Photo</label>
        <input 
            type="file" 
            id="image" 
            name="image" 
            accept="image/*"
            style="padding: 0.5rem; border: 2px dashed var(--primary); border-radius: 10px;"
        >
        <p style="font-size: 0.85rem; color: var(--gray); margin-top: 0.5rem;">
            PNG, JPG, GIF or WebP (max 5MB)
        </p>
    </div>
</div>
```

### 9. Update pets.html (My Pets page)
Make the pet cards clickable with background images:

Replace the pet card HTML with:
```html
<a href="/pets/{{ pet.id }}" class="pet-card-link">
    <div class="pet-card" style="{% if pet.image_filename %}background-image: url('/{{ pet.image_filename }}');{% else %}background: linear-gradient(135deg, #FF6B6B 0%, #FFB366 100%);{% endif %}">
        <div class="pet-card-overlay">
            <h3>{{ pet.name }}</h3>
            <p class="pet-species">{{ pet.species|capitalize }}</p>
        </div>
    </div>
</a>
```

Add this CSS to the pets.html `<style>` section:

```css
.pet-card-link {
    text-decoration: none;
    cursor: pointer;
}

.pet-card {
    background-size: cover;
    background-position: center;
    border-radius: 15px;
    overflow: hidden;
    min-height: 200px;
    position: relative;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.pet-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.pet-card-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
    padding: 1.5rem 1rem;
    color: white;
}

.pet-card-overlay h3 {
    margin: 0;
    font-size: 1.3rem;
}

.pet-species {
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
    opacity: 0.9;
}
```

### 10. Update pet_detail.html
Rename "Log Activity" button to "Mark Activity":

Replace:
```html
<a href="/pets/{{ pet.id }}/activities/new" class="btn">📝 Log Activity</a>
```

With:
```html
<a href="/pets/{{ pet.id }}/activities/new" class="btn">📝 Mark Activity</a>
```

Also display the pet image at top if it exists:

```html
{% if pet.image_filename %}
<div style="text-align: center; margin-bottom: 2rem;">
    <img src="/{{ pet.image_filename }}" alt="{{ pet.name }}" style="max-width: 300px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);">
</div>
{% endif %}
```

### 11. Delete old database
```bash
rm doodrop.db
```

### 12. Restart app
```bash
python app.py
```

Then test:
1. Add a new pet
2. Upload an image
3. See it on the pet card
4. Click card to view pet
5. See image on pet detail page

---

## Summary of Changes

✅ Pet model now has `image_filename` field
✅ File upload handler with validation
✅ Image saved to `static/uploads/pets/`
✅ Pet cards show image as background (or orange gradient if no image)
✅ Cards are clickable (removed View button)
✅ "Log Activity" renamed to "Mark Activity"
✅ Pet detail page shows larger image

---

## Next Steps

After testing this, we can add GPS tracking for walks!