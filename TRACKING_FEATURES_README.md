# New Features Added - Complaint Tracking System

## 🎉 Features Implemented

### 1. Complaint Tracking ID
- Every complaint now gets a unique tracking ID (e.g., `EDU-20260306-A1B2`)
- Format: `[DEPT]-[YYYYMMDD]-[RANDOM]`
- Department prefixes:
  - `EDU` - Education
  - `POL` - Police
  - `HLT` - Health
  - `ELC` - Electrical
  - `TRN` - Transport

### 2. Complaint Timeline
- Full status tracking from submission to resolution
- Timeline statuses:
  - **Submitted** - Initial complaint registration
  - **Assigned** - Assigned to an officer
  - **In Progress** - Work in progress
  - **Resolved** - Issue fixed
  - **On Hold** - Temporarily paused
  - **Rejected** - Not valid/actionable
- Each timeline entry includes:
  - Status name
  - Notes/comments
  - Who made the change
  - Timestamp

### 3. Citizen Feedback System
- After complaint resolution, citizens can:
  - Rate satisfaction (1-5 stars)
  - Add optional comments
  - View their submitted feedback
- Feedback is linked to the complaint tracking ID

---

## 📦 Installation & Setup

### Step 1: Run Database Migration

After setting up your initial database with `database.sql`, run the new migration:

```bash
# Using psql command line
psql -U postgres -d citizen_bridge -f database_migration_tracking.sql

# OR using Python
python -c "import psycopg2; conn = psycopg2.connect('dbname=citizen_bridge user=postgres password=nsrit'); cur = conn.cursor(); cur.execute(open('database_migration_tracking.sql').read()); conn.commit()"
```

### Step 2: Restart Backend Server

The backend (`connet.py`) has been updated with new endpoints. Restart it:

```bash
python connet.py
```

### Step 3: Access New Features

The system is now ready! No changes needed to existing HTML pages.

---

## 🚀 Using the New Features

### For Citizens

#### Tracking Your Complaint

1. **Get Tracking ID**: When you submit a complaint, you'll receive a tracking ID
2. **Visit Tracking Page**: Open `track_complaint.html` in your browser at:
   ```
   http://localhost:8000/track_complaint.html
   ```
3. **Enter Tracking ID**: Type your tracking ID (e.g., `EDU-20260306-A1B2`)
4. **View Details**: See real-time status, timeline, and location

#### Submitting Feedback

1. **Track Your Complaint**: Use the tracking page
2. **Wait for Resolution**: Feedback form appears only after status = "Resolved"
3. **Rate & Comment**: 
   - Select 1-5 stars
   - Add optional comment about your experience
4. **Submit**: Your feedback is saved and visible on future tracking

### For Admins

#### Updating Complaint Status

1. **Open Admin Panel**: `admin_health.html` (or other department)
2. **Find Complaint**: Locate the complaint you want to update
3. **Click "Update Status"**: Opens status dialog
4. **Select New Status**: Choose from:
   - Submitted
   - Assigned
   - In Progress
   - Resolved
   - On Hold
   - Rejected
5. **Add Notes**: Optional notes about the status change
6. **Submit**: Status updates and timeline entry is created automatically

#### Viewing Timeline

1. **Open Admin Panel**
2. **Click "📋 Timeline"** button on any complaint card
3. **View History**: See complete status change history with:
   - All status transitions
   - Notes from each update
   - Who made changes
   - Timestamps

---

## 🔧 API Endpoints (New)

### Track Complaint (Public)
```
GET /api/track/<tracking_id>
```
Returns complaint details, timeline, and feedback (if any)

**Example Response:**
```json
{
  "success": true,
  "complaint": {
    "id": 1,
    "tracking_id": "EDU-20260306-A1B2",
    "status": "In Progress",
    "department": "Education",
    "timeline": [
      {
        "status": "Submitted",
        "notes": "Complaint registered",
        "changed_by": "Citizen",
        "timestamp": "2026-03-06 10:30:00"
      },
      {
        "status": "In Progress",
        "notes": "Assigned to officer",
        "changed_by": "Admin",
        "timestamp": "2026-03-06 14:20:00"
      }
    ],
    "feedback": null
  }
}
```

### Update Complaint Status
```
POST /api/complaints/<department>/<complaint_id>/update-status
```
**Body:**
```json
{
  "status": "In Progress",
  "notes": "Engineer dispatched to location",
  "changed_by": "Health Admin"
}
```

### Submit Feedback
```
POST /api/complaints/feedback
```
**Body:**
```json
{
  "tracking_id": "EDU-20260306-A1B2",
  "rating": 5,
  "comment": "Very satisfied with the response",
  "citizen_name": "Anonymous"
}
```

---

## 📁 Files Modified/Added

### New Files
- `database_migration_tracking.sql` - Database schema updates
- `track_complaint.html` - Public tracking page
- `TRACKING_FEATURES_README.md` - This file

### Modified Files
- `connet.py` - Added tracking, timeline, and feedback endpoints
- `admin_health.html` - Added status update and timeline viewing UI

### Files to Update (Optional)
You can apply the same admin panel changes to:
- `admin_education.html`
- `admin_police.html`
- `admin_electrical.html`
- `admin_transport.html`

---

## 🎨 UI Components

### Tracking Page Features
- ✅ Search by tracking ID
- ✅ Real-time status display
- ✅ Visual timeline with icons
- ✅ Location information
- ✅ Feedback submission form (for resolved complaints)
- ✅ Mobile responsive design

### Admin Panel Enhancements
- ✅ Tracking ID badge on each complaint
- ✅ Status update dropdown with 6 statuses
- ✅ Timeline viewer modal
- ✅ Color-coded status indicators
- ✅ Notes field for status changes

---

## 📊 Database Schema Changes

### New Tables
1. **complaint_timeline** - Stores all status changes
2. **complaint_feedback** - Stores citizen ratings and comments

### Modified Tables
All complaint tables now have:
- `tracking_id VARCHAR(20) UNIQUE` - Unique tracking identifier
- `assigned_to VARCHAR(200)` - Officer assigned (future use)
- `resolved_at TIMESTAMP` - When complaint was resolved

---

## 🔐 Security Notes

1. **Tracking ID Access**: Anyone with a tracking ID can view complaint status (by design)
2. **Personal Data**: Aadhaar numbers are masked in tracking view (shows `1234****78`)
3. **Admin Actions**: Status updates are logged with who made the change
4. **Feedback**: One feedback per complaint (prevents spam)

---

## 🐛 Troubleshooting

### "Tracking ID not found"
- Check if database migration ran successfully
- Verify tracking_id was generated (check database)
- Ensure backend server is running

### "Cannot update status"
- Check backend server logs
- Verify complaint exists in the correct department table
- Ensure status value is one of the valid options

### "Feedback submission failed"
- Complaint must be in "Resolved" status
- Check if feedback already exists (only one per complaint)
- Verify tracking ID is correct

---

## 🚀 Next Steps (Future Enhancements)

1. **Email Notifications**: Send tracking ID to citizen's email
2. **SMS Alerts**: Notify citizens when status changes
3. **Officer Assignment**: Add officer dropdown in admin panel
4. **Analytics Dashboard**: Track average resolution time per department
5. **Feedback Reports**: Admin view of all ratings and comments
6. **Export Timeline**: Download timeline as PDF

---

## 📞 Support

For issues or questions:
1. Check backend logs: `python connet.py`
2. Check browser console (F12) for JavaScript errors
3. Verify database connection in `db_manager.py`

---

**Version**: 1.0  
**Date**: March 6, 2026  
**Status**: ✅ Production Ready
