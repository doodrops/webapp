# DooDrop Caretaker Invitations - Email-Based System 🤝

## What Changed?

The caretaker system now supports **both workflows**:

### ✅ Workflow 1: Invite Without Account
- Owner enters caretaker's email
- **Caretaker doesn't need an account yet**
- Invitation saved as "Pending"
- When caretaker creates account with that email, they automatically get access

### ✅ Workflow 2: Invite With Account
- Owner enters caretaker's email
- **Caretaker already has account**
- Automatically marked as "Accepted"
- Caretaker can immediately see and help manage the pet

---

## How to Use

### Step 1: Add a Caretaker

1. Go to pet detail page
2. Scroll to "👥 Caretakers"
3. Click "➕ Add Caretaker"
4. Enter caretaker's email address
5. Click "➕ Add Caretaker"

### Step 2: What Happens?

#### If They Have an Account
- ✅ Email shows status: "✅ Accepted"
- ✅ They can immediately see the pet
- ✅ They can immediately log activities

#### If They Don't Have an Account
- ⏳ Email shows status: "⏳ Pending Invite"
- ℹ️ You should send them the DooDrop link separately
- ✅ Once they create an account with that email, status changes to "✅ Accepted"

---

## Technical Details

### Database Changes

**Caretaker Table** now has:
```sql
- id (primary key)
- user_id (nullable - null if pending invite)
- pet_id (foreign key)
- email (required - for both existing users and invites)
- status (pending | accepted | rejected)
- invited_at (datetime)
- accepted_at (datetime, nullable)
```

### Automatic Acceptance

When a pending caretaker creates an account:
1. App matches email addresses
2. User_id is populated
3. Status changes to "accepted"
4. accepted_at timestamp is set
5. User sees the pet immediately

---

## User Scenarios

### Scenario 1: Family Pet with Dog Walker

**Owner:** Sarah (sarah@email.com)
**Dog walker:** Mike (mike@email.com) - no DooDrop account yet

1. Sarah adds mike@email.com as caretaker
2. Status shows "⏳ Pending Invite"
3. Sarah texts Mike: "Join DooDrop to help manage Buddy!"
4. Mike goes to doodrop.app and signs up with mike@email.com
5. Mike logs in - Buddy now appears in his pets! 🐕
6. Mike logs a walk activity
7. Sarah sees Mike's activity

### Scenario 2: Pet Sitter Network

**Owner:** Tom (tom@email.com)
**Sitters:** 
- Alice (alice@sitco.com) - already has DooDrop account ✅
- Bob (bob@sitco.com) - doesn't have account yet ⏳

1. Tom adds alice@sitco.com → "✅ Accepted" (immediately usable)
2. Tom adds bob@sitco.com → "⏳ Pending Invite"
3. Alice can see the pet right away, logs activities
4. Tom shares DooDrop with Bob
5. Bob creates account with bob@sitco.com
6. Bob sees the pet automatically
7. Both can now log activities for the same pet

### Scenario 3: Veterinary Clinic

**Owner:** Pet owner (owner@email.com)
**Assistant:** Clinic helper (helper@clinic.com) - shares clinic email

1. Owner adds helper@clinic.com
2. If clinic has account → "✅ Accepted"
3. If not → "⏳ Pending Invite"
4. Once assistant creates account, can log care activities
5. All records visible to owner for review

---

## Removing Caretakers

Works same as before:
1. Go to pet detail
2. Find caretaker in list
3. Click "Remove"
4. Confirmation dialog
5. ✅ Removed immediately

**For pending invites:** Removing a pending invite means if they later create an account with that email, they won't gain access.

---

## Permissions

| Action | Owner | Caretaker (Accepted) | Caretaker (Pending) | Admin |
|--------|-------|-------------------|----------------|-------|
| See pet | ✅ | ✅ | ❌ | ✅ |
| Log activities | ✅ | ✅ | ❌ | ✅ |
| Edit own activities | ✅ | ✅ | ❌ | ✅ |
| Edit pet info | ✅ | ❌ | ❌ | ✅ |
| Delete pet | ✅ | ❌ | ❌ | ✅ |
| Add caretakers | ✅ | ❌ | ❌ | ✅ |
| Remove caretakers | ✅ | ❌ | ❌ | ✅ |

**Key:** Pending caretakers have NO access until they create an account.

---

## Error Handling

### Error: "Email already a caretaker for this pet"
- Someone with this email is already assigned
- Either pending invite or accepted caretaker

**Solution:** Remove them first if you want to re-invite

### Error: "Cannot add the pet owner as a caretaker"
- You tried to add yourself as caretaker
- Owner and caretaker are different roles

**Solution:** Use a different email

### Error: "Email is required"
- You didn't enter an email address

**Solution:** Fill in the email field

---

## Future Enhancements

With email invitations, we can add:

### Notification System
- Email sent when invited as caretaker
- Email when caretaker logs activity
- Weekly digest of pet activities
- Reminders for pending invites

### Acceptance Flow
- Caretaker receives invite email
- Email contains accept/reject link
- Rejected invites prevent auto-acceptance
- Option to cancel pending invites

### Multiple Email Support
- User can add alternative emails
- All match for caretaker lookups

### Activity Permissions
- Caretaker can log walks, meals, bathroom
- Owner can restrict caretaker to certain activity types
- Admin approval workflow for sensitive activities

---

## Testing the Feature

### Test 1: Invite Non-Existent User
```
1. Login as owner
2. Add caretaker with email: newuser@example.com
3. See "⏳ Pending Invite"
4. Logout
5. Register new account: newuser@example.com
6. Login as newuser
7. See pet in "Your Pets"
```

### Test 2: Invite Existing User
```
1. Create 2 accounts first
2. Login as owner
3. Add caretaker with existing user's email
4. See "✅ Accepted"
5. Logout
6. Login as caretaker
7. Immediately see pet
```

### Test 3: Remove Pending Invite
```
1. Add caretaker with random@example.com
2. See "⏳ Pending Invite"
3. Click Remove
4. Invite disappears
5. If random@example.com creates account later
6. They won't see the pet
```

### Test 4: Re-Invite Removed Caretaker
```
1. Invite user and accept
2. Remove caretaker
3. Try to invite same email again
4. Should work - no duplicate error
```

---

## Database Migration Notes

If you're upgrading from the old system:

**Old schema:**
```sql
user_id (required)
pet_id (required)
added_at (timestamp)
unique(user_id, pet_id)
```

**New schema:**
```sql
user_id (nullable)
pet_id (required)
email (required) - NEW
status (required, default='pending') - NEW
invited_at (timestamp)
accepted_at (nullable) - NEW
unique(email, pet_id) - CHANGED
```

**Migration strategy:**
1. Add new columns
2. Copy existing user emails to caretaker.email
3. Set status='accepted' for existing records
4. Remove old unique constraint
5. Add new unique constraint

---

## Files Updated

- **doodrop_app.py**
  - Caretaker model: Added email, status, invited_at, accepted_at fields
  - add_caretaker route: Now creates invites for both existing and new users
  - owner_or_caretaker function: Checks status='accepted' only

- **templates/pet_detail.html**
  - Shows email addresses instead of usernames
  - Shows "✅ Accepted" or "⏳ Pending Invite" status
  - Added CSS for status display

- **templates/add_caretaker.html**
  - Explains both invitation workflows
  - Clearer messaging about what happens

---

## You're Ready!

The caretaker system now works for real-world scenarios:

✅ Invite anyone by email
✅ Works whether they have account or not  
✅ Automatic access once they sign up
✅ Clear status indicators
✅ Better permissions model

Try it out! 🐾