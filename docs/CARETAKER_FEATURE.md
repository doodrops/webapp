# DooDrop Caretaker Feature - Setup & Testing Guide 🤝

## What's a Caretaker?

A caretaker is someone who can help manage a pet's care activities but has limited permissions:

| Action | Owner | Caretaker | Admin |
|--------|-------|-----------|-------|
| Create pet | ✅ | ❌ | ✅ |
| Edit pet info | ✅ | ❌ | ✅ |
| Delete pet | ✅ | ❌ | ✅ |
| **Log activities** | ✅ | ✅ | ✅ |
| **Edit own activities** | ✅ | ✅ | ✅ |
| Delete own activities | ✅ | ✅ | ✅ |
| Add/remove caretakers | ✅ | ❌ | ✅ |

Perfect for:
- Family members helping with daily care
- Dog walkers
- Pet sitters
- Veterinary assistants

---

## Why You Got "User not found"

When you tried to add a caretaker, you got this error because:
1. You only have **one account** (testuser)
2. The caretaker feature needs **at least 2 user accounts**
3. The app was looking for another user with the email you entered
4. Since no other users exist, it returned "User not found"

**This is expected behavior!** 

---

## How to Test the Caretaker Feature

### Step 1: Create a Second Account
This will be your "caretaker" account.

1. Logout of your current account
   - Click your username in top-right
   - Click "Logout"

2. Go to http://127.0.0.1:5000/register

3. Create a new account:
   - **Username:** caretaker_user
   - **Email:** caretaker@example.com
   - **Password:** password123
   - **Role:** Caretaker (select this!)
   - Click "Create Account"

Now you have a caretaker account, but it doesn't own any pets.

### Step 2: Switch Back to Owner Account

1. Logout (click Logout)
2. Go to http://127.0.0.1:5000/login
3. Login with **testuser** account
4. Click "My Pets" → Select your pet

### Step 3: Add the Caretaker

1. On the pet detail page, scroll down to "👥 Caretakers"
2. Click "➕ Add Caretaker"
3. Enter the caretaker's email: **caretaker@example.com**
4. Click "➕ Add Caretaker"
5. ✅ Success! You should see the caretaker listed

### Step 4: Verify Caretaker Permissions

1. Logout (Click Logout)
2. Login as **caretaker_user** (caretaker account)
3. You should see the pet in "Your Pets"
4. Click on the pet
5. You can:
   - ✅ View the pet
   - ✅ Log activities (walk, meal, bathroom)
   - ✅ See activity history
   - ❌ Cannot edit the pet
   - ❌ Cannot delete the pet
   - ❌ Cannot add/remove other caretakers

---

## Testing Different Scenarios

### Scenario 1: Error - Try to add owner as caretaker
1. Go to "Add Caretaker"
2. Enter the **owner's email** (testuser@example.com)
3. Error: "Cannot add the pet owner as a caretaker"
4. This prevents confusion about roles ✅

### Scenario 2: Error - Try to add same caretaker twice
1. Go to "Add Caretaker"
2. Enter caretaker email again
3. Error: "caretaker_user is already a caretaker for [pet name]"
4. This prevents duplicate entries ✅

### Scenario 3: Error - Try to add non-existent user
1. Go to "Add Caretaker"
2. Enter an email that doesn't have an account
3. Error: "No user found with email '[email]'. Make sure they have created a DooDrop account first."
4. Clear message about what went wrong ✅

### Scenario 4: Success - Add multiple caretakers
1. Create 3rd account (babysitter@example.com, role: Caretaker)
2. Go to "Add Caretaker"
3. Add caretaker_user@example.com
4. Go back to pet, then "Add Caretaker" again
5. Add babysitter@example.com
6. Both now listed as caretakers ✅

---

## Removal Process

### Remove a Caretaker

1. Login as **owner**
2. Go to pet detail page
3. Scroll to "👥 Caretakers"
4. Find the caretaker you want to remove
5. Click "Remove" button
6. ✅ Caretaker is removed immediately

Removed caretakers:
- Can no longer see the pet
- No longer receive activity updates
- Can be re-added later

---

## What's Fixed in This Update

### Before:
```
User clicks "Add Caretaker" with non-existent email
→ JSON error "User not found"
→ Confusing browser output
```

### After:
```
User clicks "Add Caretaker" with non-existent email
→ Friendly error message on the form page
→ Clear message: "No user found with email 'X'. Make sure they have created a DooDrop account first."
→ User can immediately try again with correct email
```

### Better Error Messages For:
- User not found
- Email is empty
- Trying to add owner as caretaker
- Trying to add duplicate caretaker

---

## Files Updated

- **doodrop_app.py**: Better error handling in add_caretaker route
- **templates/add_caretaker.html**: Display error messages on the form

No changes to database or other features!

---

## Real-World Use Cases

### Use Case 1: Family Pet
```
Owner: Mom (email: mom@family.com)
Caretakers:
  - Dad (dad@family.com) - logs meals
  - Teen child (teen@family.com) - logs walks
  - Dog walker (walker@service.com) - logs walks when busy

Each can see the pet and log activities
Mom owns it, so only she can add/remove caretakers or delete pet
```

### Use Case 2: Pet Sitting Service
```
Owner: Client (email: client@email.com)
Caretaker: Pet sitter (email: sitter@sitco.com)

Sitter logs all activities while watching pet
Can update notes but can't delete pet or invite others
Client can add multiple sitters for different pets
```

### Use Case 3: Veterinary Clinic
```
Owner: Pet owner (email: owner@email.com)
Caretaker: Vet assistant (email: assistant@clinic.com)

During boarding, assistant logs meals, medications, observations
Vet can review history but can't delete records (only owner/admin can)
After boarding, owner removes caretaker
```

---

## Full Testing Checklist

- [ ] Create 2nd account (caretaker role)
- [ ] Switch to owner account
- [ ] Add caretaker successfully
- [ ] See caretaker in pet detail
- [ ] Login as caretaker
- [ ] View pet (caretaker can see it)
- [ ] Log an activity as caretaker
- [ ] Try to edit pet (should be disabled)
- [ ] Try to delete pet (should be disabled)
- [ ] Login as owner
- [ ] See activity logged by caretaker
- [ ] Remove caretaker
- [ ] Login as (former) caretaker
- [ ] Verify pet no longer visible

All passing? You're good to go! ✅

---

## Next Steps

1. Test the caretaker feature with the steps above
2. Try error scenarios to see better error messages
3. When satisfied, deploy to Fly.io
4. Have real users create accounts and test the feature

Questions about caretaker permissions? Check the table at the top of this guide!

Happy caring! 🐾