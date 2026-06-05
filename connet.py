#omm namah shivaya
print("Starting Flask server...")
from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import psycopg2
import requests
import json
import secrets
from datetime import datetime

app = Flask(__name__)
CORS(app)

MODEL = "minimax-m3:cloud"

DB_CONFIG = {
    'dbname': os.environ.get('CB_DB_NAME', 'citizen_bridge'),
    'user': os.environ.get('CB_DB_USER', 'postgres'),
    'password': os.environ.get('CB_DB_PASSWORD', 'nsrit'),
    'host': os.environ.get('CB_DB_HOST', 'localhost'),
    'port': int(os.environ.get('CB_DB_PORT', 5432))
}
print('DB_CONFIG:', {k: (v if k!='password' else '***') for k,v in DB_CONFIG.items()})

DEPT_TABLES = {
    'education': 'complaints_education',
    'police': 'complaints_police',
    'health': 'complaints_health',
    'electrical': 'complaints_electrical',
    'transport': 'complaints_transport'
}

def get_db_connection():
    return psycopg2.connect(
        **DB_CONFIG,
        sslmode='require'
    )

def generate_tracking_id(department):
    """Generate unique tracking ID: DEPT-YYYYMMDD-XXXX"""
    dept_prefixes = {
        'education': 'EDU',
        'police': 'POL',
        'health': 'HLT',
        'electrical': 'ELC',
        'transport': 'TRN'
    }
    prefix = dept_prefixes.get(department.lower(), 'GEN')
    date_str = datetime.now().strftime('%Y%m%d')
    random_suffix = secrets.token_hex(2).upper()  # 4 character hex
    return f"{prefix}-{date_str}-{random_suffix}"

def add_timeline_entry(conn, complaint_id, department, status, notes="", changed_by="System"):
    """Add entry to complaint timeline"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO complaint_timeline (complaint_id, department, status, notes, changed_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (complaint_id, department, status, notes, changed_by))
        cursor.close()
    except Exception as e:
        print(f"Timeline entry error: {e}")

# ---------------- REGISTER ----------------

@app.route("/api/register", methods=["POST"])
def register_citizen():
    try:
        data = request.json

        full_name = data.get('fullName', '')
        first_name = full_name

        address = data.get('address', '')
        mandal = data.get('mandal', '')
        district = data.get('district', '')
        state = data.get('state', '')
        pincode = data.get('pincode', '')
        phone = data.get('phone', '')
        email = data.get('email', '')
        username = data.get('username', '')
        password = data.get('password', '')
        aadhar = data.get('aadhar', '')

        full_address = f"{address}, {mandal}, {district}"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO citizens 
            (email, username, password_hash, first_name, phone, address, city, state, postal_code, aadhar_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (email, username, password, first_name, phone, full_address, district, state, pincode, aadhar))

        citizen_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "citizen_id": citizen_id}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- LOGIN ----------------

@app.route("/api/login", methods=["POST"])
def login_citizen():
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, password_hash, first_name 
            FROM citizens WHERE username = %s
        """, (username,))


        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user[2] == password:
            return jsonify({
                "success": True,
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "name": user[3]
                }
            }), 200
        else:
            return jsonify({"success": False, "message": "Invalid username or password"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- DEPARTMENT LOGIN (for admin panels) ----------------
@app.route("/api/department-login", methods=["POST"])
def department_login():
    try:
        data = request.json or {}
        name = (data.get('name') or '').strip()
        dept_id = (data.get('id') or '').strip()

        if not name or not dept_id:
            return jsonify({"success": False, "message": "Name and ID are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Try matching by officer_name + department_code or username (case-insensitive)
        # Join to departments to get a canonical department name (slug)
        cursor.execute("""
            SELECT d.name AS dept_name, o.department_code
            FROM department_officers o
            LEFT JOIN departments d ON o.department_id = d.id
            WHERE lower(o.officer_name) = lower(%s)
              AND (lower(o.department_code) = lower(%s) OR lower(o.username) = lower(%s))
            LIMIT 1
        """, (name, dept_id, dept_id))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            dept_name = (row[0] or '').lower()
            dept_code_field = (row[1] or '').lower()

            # Map department display names to expected slugs used by admin pages
            name_to_slug = {
                'police': 'police',
                'transport': 'transport',
                'education': 'education',
                'electrical': 'electrical',
                'health & sanitation': 'health',
                'health': 'health'
            }

            slug = None
            if dept_name in name_to_slug:
                slug = name_to_slug[dept_name]
            elif dept_code_field in ['police','transport','education','electrical','health']:
                slug = dept_code_field
            else:
                # fallback: attempt to extract first word
                slug = (dept_name.split()[0] if dept_name else dept_code_field)

            return jsonify({"success": True, "department": slug}), 200
        else:
            return jsonify({"success": False, "message": "Invalid name or ID"}), 401

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Helper function to call Ollama API directly (instead of ollama.chat)
def call_ollama_api(prompt):
    try:
        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                'model': MODEL,
                'prompt': prompt,
                'stream': False
            },
            timeout=90
        )
        result = response.json()
        return result.get('response', '').strip()
    except Exception as e:
        return f"Error: {str(e)}"

# AI ANALYSIS ENDPOINTS

@app.route("/api/ai-analyze", methods=["POST"])
def ai_analyze_complaint():
    """Analyze complaint for:
    - Main Problem
    - Key Points
    - Unique Aspects
    - Priority Level
    - Recommended Actions
    """
    try:
        data = request.json
        problem = data.get('problem', '')
        
        if not problem:
            return jsonify({'success': False, 'message': 'Problem description required'}), 400
        
        prompt = f"""Analyze this citizen complaint:
"{problem}"

Provide analysis in this format:
Main Problem: [key issue]
Key Points: [important details]
Unique Aspects: [special concerns]
Priority: [Low/Medium/High]
Recommended Action: [solution]"""
        
        analysis = call_ollama_api(prompt)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route("/api/ai-categorize", methods=["POST"])
def ai_categorize_complaint():
    """Categorize complaint to appropriate department"""
    try:
        data = request.json
        problem = data.get('problem', '')
        
        if not problem:
            return jsonify({'success': False, 'message': 'Problem description required'}), 400
        
        prompt = f"""Which government department should handle this complaint?

Complaint: "{problem}"

Departments:
1. Education
2. Police
3. Health
4. Electrical
5. Transport

Respond with ONLY the department name."""
        
        category = call_ollama_api(prompt)
        
        # Map to lowercase for consistency
        dept_map = {
            'education': 'education',
            'police': 'police',
            'health': 'health',
            'electrical': 'electrical',
            'transport': 'transport'
        }
        
        department = None
        for key in dept_map:
            if key.lower() in category.lower():
                department = key
                break
        
        if not department:
            department = category.lower().split()[0] if category else 'unknown'
        
        return jsonify({
            'success': True,
            'category': department,
            'raw_response': category
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route("/api/ai-priority", methods=["POST"])
def ai_assess_priority():
    """Assess complaint priority level"""
    try:
        data = request.json
        problem = data.get('problem', '')
        
        if not problem:
            return jsonify({'success': False, 'message': 'Problem description required'}), 400
        
        prompt = f"""Rate the urgency/priority of this complaint on a scale of Low, Medium, or High.

Complaint: "{problem}"

Respond with ONLY: Low, Medium, or High"""
        
        priority = call_ollama_api(prompt).strip()
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        if priority.lower() not in valid_priorities:
            priority = 'medium'  # default
        
        return jsonify({
            'success': True,
            'priority': priority.lower()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route("/api/ai-action-plan", methods=["POST"])
def ai_get_action_plan():
    """Get AI recommended action plan for complaint"""
    try:
        data = request.json
        problem = data.get('problem', '')
        department = data.get('department', '')
        
        if not problem:
            return jsonify({'success': False, 'message': 'Problem description required'}), 400
        
        dept_context = f" in the {department} department" if department else ""
        prompt = f"""Create a brief action plan to resolve this complaint{dept_context}.

Complaint: "{problem}"

Provide:
1. Immediate Action
2. Follow-up Steps
3. Expected Timeline"""
        
        action_plan = call_ollama_api(prompt)
        
        return jsonify({
            'success': True,
            'action_plan': action_plan
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# OLD AI ENDPOINTS (FOR BACKWARD COMPATIBILITY)

@app.route("/ai-analyse-problem", methods=["POST"])
def ai_analyse_problem():
    data = request.json
    problem = data.get("problem", "")

    prompt = f"""Summarize this problem in one sentence, include location if mentioned.
Problem: {problem}"""
    
    analysis = call_ollama_api(prompt)
    return jsonify({"analysis": analysis})


@app.route("/ai-suggest", methods=["POST"])
def ai_suggest():
    data = request.json
    problem = data.get("problem", "").lower()
    
    # Keywords for each department
    keywords = {
        'Health': ['health', 'hospital', 'disease', 'medical', 'doctor', 'patient', 'illness', 'medicine'],
        'Transport': ['road', 'traffic', 'vehicle', 'bus', 'transport', 'highway', 'street', 'pothole'],
        'Electrical': ['electricity', 'power', 'current', 'bill', 'electric', 'light', 'meter', 'voltage'],
        'Police': ['police', 'crime', 'theft', 'assault', 'abuse', 'violence', 'law', 'justice'],
        'Education': ['school', 'college', 'education', 'student', 'admission', 'exam', 'teacher', 'university']
    }
    
    # Check keywords first (faster, more reliable)
    for dept, words in keywords.items():
        for word in words:
            if word in problem:
                return jsonify({"sector": dept})
    
    # If no keywords match, ask AI
    prompt = f"""{problem}
ONLY answer with ONE of these: Health, Transport, Electrical, Police, Education"""

    sector = call_ollama_api(prompt).strip().lower()
    
    # Extract department from response
    if 'health' in sector:
        return jsonify({"sector": "Health"})
    elif 'transport' in sector or 'road' in sector:
        return jsonify({"sector": "Transport"})
    elif 'electrical' in sector or 'electricity' in sector or 'power' in sector:
        return jsonify({"sector": "Electrical"})
    elif 'police' in sector or 'crime' in sector:
        return jsonify({"sector": "Police"})
    elif 'education' in sector or 'school' in sector:
        return jsonify({"sector": "Education"})
    else:
        return jsonify({"sector": "Transport"})  # Default


# ---------------- SUBMIT COMPLAINT ----------------

@app.route("/api/submit-complaint", methods=["POST"])
def submit_complaint():
    try:
        data = request.json

        department = data.get('department', '').lower()
        table_name = DEPT_TABLES.get(department)

        if not table_name:
            return jsonify({"success": False, "message": "Invalid department"}), 400

        # Generate unique tracking ID
        tracking_id = generate_tracking_id(department)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            INSERT INTO {table_name}
            (aadhaar, phone, address, mandal, district, state, pincode, problem_description, proof_image, tracking_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('aadhaar'),
            data.get('phone'),
            data.get('address'),
            data.get('mandal'),
            data.get('district'),
            data.get('state'),
            data.get('pincode'),
            data.get('problem_description'),
            data.get('proof_image'),
            tracking_id,
            'Submitted'
        ))

        complaint_id = cursor.fetchone()[0]

        # Add timeline entry
        add_timeline_entry(conn, complaint_id, department, 'Submitted', 
                          f"Complaint registered from {data.get('district')}", "Citizen")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Complaint Stored Successfully: ID={complaint_id}, Tracking={tracking_id}")

        return jsonify({
            "success": True, 
            "complaint_id": complaint_id,
            "tracking_id": tracking_id,
            "message": f"Complaint submitted successfully. Your tracking ID is: {tracking_id}"
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- FETCH COMPLAINTS ----------------

@app.route("/api/complaints/<department>", methods=["GET"])
def get_complaints(department):
    try:
        table_name = DEPT_TABLES.get(department.lower())
        if not table_name:
            return jsonify({"success": False, "message": "Invalid department"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT id, aadhaar, phone, address, mandal, district, state, pincode,
                   problem_description, proof_image, status, tracking_id, created_at
            FROM {table_name}
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        complaints = []

        for row in rows:
            complaints.append({
                "id": row[0],
                "aadhaar": row[1],
                "phone": row[2],
                "address": row[3],
                "mandal": row[4],
                "district": row[5],
                "state": row[6],
                "pincode": row[7],
                "problem_description": row[8],
                "proof_image": row[9],
                "status": row[10],
                "tracking_id": row[11],
                "created_at": row[12].strftime("%Y-%m-%d %H:%M:%S") if row[12] else ""
            })

        return jsonify(complaints), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/complaints/<department>/<int:complaint_id>/resolve", methods=["POST"])
def resolve_complaint(department, complaint_id):
    try:
        table_name = DEPT_TABLES.get(department.lower())
        if not table_name:
            return jsonify({"success": False, "message": "Invalid department"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            UPDATE {table_name}
            SET status = %s
            WHERE id = %s
            """,
            ("Resolved", complaint_id)
        )

        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Complaint not found"}), 404

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Complaint status updated"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ---------------- AI ANALYSIS PROXY (for admin panels) ----------------

@app.route("/api/ai-analyze-proxy", methods=["POST"])
def ai_analyze_proxy():
    """
    Proxy endpoint for AI analysis to avoid CORS issues
    Admin panels call this endpoint instead of directly calling Ollama
    """
    try:
        data = request.json
        problem_description = data.get('problem', '')
        
        if not problem_description:
            return jsonify({"success": False, "error": "No problem description provided"}), 400
        
        print(f"AI Analysis Request: {problem_description[:100]}...")
        
        prompt = (
            "Analyze this problem and provide a clear, concise one-line problem definition:\n\n"
            f"Problem: {problem_description}\n\n"
            "Provide only one sentence that clearly defines the core issue."
        )

        # Try fast/default model first, then graceful fallback models.
        # This avoids long hangs when a heavy model is unavailable/slow.
        candidate_models = [MODEL, 'phi:latest', 'tinyllama']
        tried_models = []

        for model_name in candidate_models:
            if model_name in tried_models:
                continue
            tried_models.append(model_name)

            try:
                response = requests.post(
                    'http://127.0.0.1:11434/api/generate',
                    json={
                        'model': model_name,
                        'prompt': prompt,
                        'stream': False
                    },
                    timeout=20
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_text = (result.get('response') or '').strip()

                    if ai_text:
                        print(f"AI Response ({model_name}): {ai_text[:100]}...")
                        return jsonify({
                            "success": True,
                            "response": ai_text,
                            "model": result.get('model', model_name)
                        }), 200
            except requests.exceptions.Timeout:
                print(f"AI timeout on model: {model_name}")
                continue
            except Exception as model_error:
                print(f"AI model error ({model_name}): {model_error}")
                continue

        return jsonify({
            "success": False,
            "error": "AI service is reachable but no model returned a response in time.",
            "models_tried": tried_models
        }), 504
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Request timed out while contacting AI models."
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "Cannot connect to Ollama. Make sure Ollama is running (ollama serve)."
        }), 503
    except Exception as e:
        print(f"AI Analysis Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ---------------- TRACKING & TIMELINE ENDPOINTS ----------------

@app.route("/api/track/<tracking_id>", methods=["GET"])
def track_complaint(tracking_id):
    """Track complaint status by tracking ID - no login required"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Search all department tables for this tracking_id
        complaint_data = None
        department = None

        for dept, table in DEPT_TABLES.items():
            cursor.execute(f"""
                SELECT id, aadhaar, phone, address, mandal, district, state, pincode,
                       problem_description, proof_image, status, tracking_id, created_at, resolved_at
                FROM {table}
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            row = cursor.fetchone()
            if row:
                department = dept
                complaint_data = {
                    "id": row[0],
                    "aadhaar": row[1][:4] + "****" + row[1][-2:] if row[1] else None,  # Mask aadhaar
                    "phone": row[2],
                    "address": row[3],
                    "mandal": row[4],
                    "district": row[5],
                    "state": row[6],
                    "pincode": row[7],
                    "problem_description": row[8],
                    "proof_image": row[9],
                    "status": row[10],
                    "tracking_id": row[11],
                    "created_at": row[12].strftime("%Y-%m-%d %H:%M:%S") if row[12] else "",
                    "resolved_at": row[13].strftime("%Y-%m-%d %H:%M:%S") if row[13] else None,
                    "department": department.capitalize()
                }
                break

        if not complaint_data:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Complaint not found with this tracking ID"}), 404

        # Get timeline
        cursor.execute("""
            SELECT status, notes, changed_by, created_at
            FROM complaint_timeline
            WHERE complaint_id = %s AND department = %s
            ORDER BY created_at ASC
        """, (complaint_data["id"], department))

        timeline_rows = cursor.fetchall()
        timeline = []
        for t_row in timeline_rows:
            timeline.append({
                "status": t_row[0],
                "notes": t_row[1],
                "changed_by": t_row[2],
                "timestamp": t_row[3].strftime("%Y-%m-%d %H:%M:%S") if t_row[3] else ""
            })

        complaint_data["timeline"] = timeline

        # Check if feedback exists
        cursor.execute("""
            SELECT rating, comment, created_at
            FROM complaint_feedback
            WHERE complaint_id = %s AND department = %s
        """, (complaint_data["id"], department))

        feedback_row = cursor.fetchone()
        if feedback_row:
            complaint_data["feedback"] = {
                "rating": feedback_row[0],
                "comment": feedback_row[1],
                "submitted_at": feedback_row[2].strftime("%Y-%m-%d %H:%M:%S") if feedback_row[2] else ""
            }
        else:
            complaint_data["feedback"] = None

        cursor.close()
        conn.close()

        return jsonify({"success": True, "complaint": complaint_data}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/complaints/<department>/<int:complaint_id>/update-status", methods=["POST"])
def update_complaint_status(department, complaint_id):
    """Update complaint status and add timeline entry"""
    try:
        data = request.json
        new_status = data.get('status')
        notes = data.get('notes', '')
        changed_by = data.get('changed_by', 'Admin')

        if not new_status:
            return jsonify({"success": False, "message": "Status is required"}), 400

        valid_statuses = ['Submitted', 'Assigned', 'In Progress', 'Resolved', 'Rejected', 'On Hold']
        if new_status not in valid_statuses:
            return jsonify({"success": False, "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400

        table_name = DEPT_TABLES.get(department.lower())
        if not table_name:
            return jsonify({"success": False, "message": "Invalid department"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Update status
        if new_status == 'Resolved':
            cursor.execute(
                f"""
                UPDATE {table_name}
                SET status = %s, resolved_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (new_status, complaint_id)
            )
        else:
            cursor.execute(
                f"""
                UPDATE {table_name}
                SET status = %s
                WHERE id = %s
                """,
                (new_status, complaint_id)
            )

        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Complaint not found"}), 404

        # Add timeline entry
        add_timeline_entry(conn, complaint_id, department.lower(), new_status, notes, changed_by)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True, 
            "message": f"Complaint status updated to: {new_status}"
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/complaints/feedback", methods=["POST"])
def submit_feedback():
    """Submit citizen feedback for resolved complaint"""
    try:
        data = request.json
        tracking_id = data.get('tracking_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        citizen_name = data.get('citizen_name', 'Anonymous')

        if not tracking_id or not rating:
            return jsonify({"success": False, "message": "Tracking ID and rating are required"}), 400

        if not (1 <= rating <= 5):
            return jsonify({"success": False, "message": "Rating must be between 1 and 5"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Find complaint by tracking_id
        complaint_id = None
        department = None

        for dept, table in DEPT_TABLES.items():
            cursor.execute(f"""
                SELECT id, status FROM {table}
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            row = cursor.fetchone()
            if row:
                complaint_id = row[0]
                complaint_status = row[1]
                department = dept

                # Check if complaint is resolved
                if complaint_status != 'Resolved':
                    cursor.close()
                    conn.close()
                    return jsonify({
                        "success": False, 
                        "message": "Feedback can only be submitted for resolved complaints"
                    }), 400
                break

        if not complaint_id:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Complaint not found"}), 404

        # Insert feedback (or update if exists)
        cursor.execute("""
            INSERT INTO complaint_feedback (complaint_id, department, rating, comment, citizen_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (complaint_id, department) 
            DO UPDATE SET rating = EXCLUDED.rating, comment = EXCLUDED.comment, created_at = CURRENT_TIMESTAMP
        """, (complaint_id, department, rating, comment, citizen_name))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Thank you for your feedback!"
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)