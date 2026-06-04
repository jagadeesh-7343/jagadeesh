# Quick Start: Testing New Tracking Features

## 🚀 Setup (5 minutes)

### Step 1: Run Database Migration
```bash
python run_migration.py
```

This will add:
- ✅ tracking_id columns to all complaint tables
- ✅ complaint_timeline table
- ✅ complaint_feedback table

### Step 2: Restart Backend
```bash
python connet.py
```

### Step 3: Start Frontend Server
```bash
python serve_admin.py
```

Your app is now ready at `http://localhost:8000`

---

## 🧪 Testing Guide

### Test 1: Submit a Complaint (Get Tracking ID)

1. Go to: `http://localhost:8000/register.html`
2. Click "Track Complaint" button (top right) OR navigate to any complaint form
3. Submit a new complaint
4. **Save the tracking ID** displayed in the success message (e.g., `EDU-20260306-A1B2`)

### Test 2: Track Complaint Without Login

1. Click the **"Track Complaint"** button (top-right orange button)
   - Or visit: `http://localhost:8000/track_complaint.html`
2. Enter your tracking ID
3. Click "Track Now"
4. ✅ **You should see:**
   - Complaint status
   - Problem description
   - Location details
   - Timeline with submission entry
   - Department name

### Test 3: Update Status (Admin)

1. Open admin panel: `http://localhost:8000/admin_health.html`
2. Find a complaint with a tracking ID
3. Click **"Update Status"** button
4. Select new status: "Assigned" or "In Progress"
5. Add notes (e.g., "Officer assigned to case")
6. Click "Update Status"
7. ✅ **Verify:**
   - Status badge changes color
   - Timeline updated with new entry

### Test 4: View Timeline

1. In admin panel, click **"📋 Timeline"** button
2. ✅ **You should see:**
   - All status changes
   - Notes for each change
   - Who made the change
   - Timestamps

### Test 5: Submit Feedback

1. Update a complaint status to **"Resolved"**
2. Go to tracking page: `http://localhost:8000/track_complaint.html`
3. Enter the resolved complaint's tracking ID
4. Scroll down to see the **feedback form**
5. Rate 1-5 stars
6. Add optional comment
7. Click "Submit Feedback"
8. ✅ **Verify:**
   - "Thank you" message appears
   - Refresh page shows submitted feedback
   - Feedback form is replaced with your rating

---

## 🎯 What's New (Summary)

| Feature | Location | What It Does |
|---------|----------|--------------|
| **Tracking ID** | All pages | Every complaint gets unique ID (e.g., EDU-20260306-A1B2) |
| **Track Button** | register.html, login.html | Orange button (top-right) links to tracking page |
| **Tracking Page** | track_complaint.html | Public page to check status without login |
| **Status Timeline** | Admin panels | Shows all status changes with notes |
| **6 Status Types** | Admin panels | Submitted → Assigned → In Progress → Resolved/Rejected/On Hold |
| **Citizen Feedback** | Tracking page | Rate resolved complaints (1-5 stars + comment) |

---

## 🎨 Status Colors

- 🔵 **Submitted** - Blue (initial state)
- 💗 **Assigned** - Pink (assigned to officer)
- 🟠 **In Progress** - Orange (work in progress)
- 🟢 **Resolved** - Green (completed)
- ⚫ **On Hold** - Gray (paused)
- 🔴 **Rejected** - Red (not actionable)

---

## 📱 Screenshots Expected

### Tracking Page
```
╔══════════════════════════════════════╗
║        🔍 Track Your Complaint       ║
║                                      ║
║  [EDU-20260306-A1B2] [Track Now]   ║
╠══════════════════════════════════════╣
║  Status: In Progress 🟠              ║
║  Tracking ID: EDU-20260306-A1B2      ║
║  Department: Education               ║
║                                      ║
║  📋 Complaint Timeline:              ║
║  ● Submitted - 2026-03-06 10:30     ║
║  ● In Progress - 2026-03-06 14:20   ║
╚══════════════════════════════════════╝
```

### Admin Panel
```
╔══════════════════════════════════════╗
║  Complaint #5   [EDU-20260306-A1B2] ║
║  Status: In Progress 🟠              ║
║                                      ║
║  [🤖 AI Analysis] [Update Status]   ║
║  [📋 Timeline]                       ║
╚══════════════════════════════════════╝
```

---

## ❓ Troubleshooting

### "Tracking ID not found"
- ✅ Run migration: `python run_migration.py`
- ✅ Submit a NEW complaint (old ones won't have tracking IDs)
- ✅ Check backend logs for errors

### Can't update status
- ✅ Make sure backend is running: `python connet.py`
- ✅ Check browser console (F12) for errors
- ✅ Verify complaint has tracking_id in database

### Feedback form not showing
- ✅ Complaint must be status = "Resolved"
- ✅ Check if feedback was already submitted (only one per complaint)

### Timeline is empty
- ✅ Status updates create timeline entries
- ✅ Old complaints won't have timeline unless you update their status

---

## 🎉 Success Checklist

- [ ] Migration ran without errors
- [ ] Backend shows no errors when starting
- [ ] "Track Complaint" button visible on register.html and login.html
- [ ] Can submit new complaint and receive tracking ID
- [ ] Can track complaint on track_complaint.html
- [ ] Can update status in admin panel
- [ ] Timeline shows status history
- [ ] Can submit feedback on resolved complaints
- [ ] Feedback displays correctly after submission

---

## 📊 Database Quick Check

```sql
-- Check if tracking_id columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'complaints_health' AND column_name = 'tracking_id';

-- Check if new tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('complaint_timeline', 'complaint_feedback');

-- View a sample tracking ID
SELECT tracking_id, status, problem_description 
FROM complaints_health LIMIT 1;

-- View timeline for complaint ID 1
SELECT * FROM complaint_timeline 
WHERE complaint_id = 1 AND department = 'health';
```

---

**Need More Help?** Check `TRACKING_FEATURES_README.md` for detailed API documentation.
