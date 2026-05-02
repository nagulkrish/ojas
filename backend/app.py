from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow HTML pages to talk to this backend

# ─────────────────────────────────────────
# Database Connection
# ─────────────────────────────────────────
def get_db():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', 5432),
        sslmode='require'
    )
    return conn

def query(sql, params=None):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    results = cur.fetchall()
    conn.close()
    return [dict(r) for r in results]

def execute(sql, params=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

# Home - test if backend is working
@app.route('/')
def home():
    return jsonify({'message': 'OJAS 2K26 Backend is running!', 'status': 'ok'})

# ── EVENTS ──────────────────────────────

# GET all events
@app.route('/api/events', methods=['GET'])
def get_events():
    fest = request.args.get('fest', 'ojas')

    if fest == 'srujana':
        table = 'srujana_events'
    elif fest == 'samyuti':
        table = 'samyuti_events'
    else:
        table = 'events'

    rows = query(f"SELECT * FROM {table} ORDER BY date ASC")
    return jsonify(rows)

# GET single event
@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    rows = query("SELECT * FROM events WHERE event_id = %s", (event_id,))
    if not rows:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(rows[0])

# POST add new event
@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    execute("""
        INSERT INTO events (event_name, date, venue, time, organizer_club, event_type, school)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get('event_name'),
        data.get('date'),
        data.get('venue'),
        data.get('time'),
        data.get('organizer_club'),
        data.get('event_type'),
        data.get('school')
    ))
    return jsonify({'message': 'Event added successfully!'}), 201

# ── PARTICIPANTS ─────────────────────────

# GET all participants
@app.route('/api/participants', methods=['GET'])
def get_participants():
    rows = query("SELECT * FROM participants ORDER BY name ASC")
    return jsonify(rows)

# GET participant by name or email (search)
@app.route('/api/participants/search', methods=['GET'])
def search_participant():
    q = request.args.get('q', '')
    rows = query("""
        SELECT * FROM participants
        WHERE name ILIKE %s OR email ILIKE %s
    """, (f'%{q}%', f'%{q}%'))
    return jsonify(rows)

# POST add new participant
@app.route('/api/participants', methods=['POST'])
def add_participant():
    data = request.json
    try:
        execute("""
            INSERT INTO participants (name, email, phone, school)
            VALUES (%s, %s, %s, %s)
        """, (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('school')
        ))
        return jsonify({'message': 'Participant added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': 'Email already exists!'}), 400

# ── REGISTRATIONS ────────────────────────

# GET registrations for a participant
@app.route('/api/registrations/<int:participant_id>', methods=['GET'])
def get_registrations(participant_id):
    rows = query("""
        SELECT r.registration_id, e.event_name, e.date, e.venue, e.time
        FROM registrations r
        JOIN events e ON r.event_id = e.event_id
        WHERE r.participant_id = %s
    """, (participant_id,))
    return jsonify(rows)

# ── RESULTS ──────────────────────────────

# GET all results
@app.route('/api/results', methods=['GET'])
def get_results():
    rows = query("""
        SELECT res.result_id, res.winner_name, res.position, res.award,
               e.event_name
        FROM results res
        JOIN registrations r ON res.registration_id = r.registration_id
        JOIN events e ON r.event_id = e.event_id
        ORDER BY e.event_name, res.position
    """)
    return jsonify(rows)

# GET results for a participant
@app.route('/api/results/participant/<int:participant_id>', methods=['GET'])
def get_participant_results(participant_id):
    rows = query("""
        SELECT res.winner_name, res.position, res.award, e.event_name
        FROM results res
        JOIN registrations r ON res.registration_id = r.registration_id
        JOIN events e ON r.event_id = e.event_id
        WHERE r.participant_id = %s
    """, (participant_id,))
    return jsonify(rows)

# ── DASHBOARD ANALYTICS ──────────────────

# GET dashboard stats
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():

    # Total counts
    totals = query("""
        SELECT
            (SELECT COUNT(*) FROM events) as total_events,
            (SELECT COUNT(*) FROM participants) as total_participants,
            (SELECT COUNT(*) FROM registrations) as total_registrations,
            (SELECT COUNT(*) FROM results) as total_winners
    """)[0]

    # Participation per school
    school_stats = query("""
        SELECT p.school, COUNT(r.registration_id) as total
        FROM participants p
        JOIN registrations r ON p.participant_id = r.participant_id
        GROUP BY p.school
        ORDER BY total DESC
    """)

    # Events per date
    date_stats = query("""
        SELECT date, COUNT(*) as event_count
        FROM events
        WHERE date IS NOT NULL
        GROUP BY date
        ORDER BY date
    """)

    # Top 5 events by registrations
    top_events = query("""
        SELECT e.event_name, COUNT(r.registration_id) as total
        FROM events e
        LEFT JOIN registrations r ON e.event_id = r.event_id
        GROUP BY e.event_name
        ORDER BY total DESC
        LIMIT 5
    """)

    # Event type split
    type_split = query("""
        SELECT event_type, COUNT(*) as count
        FROM events
        GROUP BY event_type
    """)

    # Students in multiple events
    multi_event = query("""
        SELECT COUNT(*) as count FROM (
            SELECT participant_id
            FROM registrations
            GROUP BY participant_id
            HAVING COUNT(*) > 1
        ) sub
    """)[0]

    return jsonify({
        'totals': totals,
        'school_stats': school_stats,
        'date_stats': date_stats,
        'top_events': top_events,
        'type_split': type_split,
        'multi_event_students': multi_event['count']
    })

# ── STUDENT LOOKUP ───────────────────────

# GET full student profile (registrations + results)
@app.route('/api/student', methods=['GET'])
def get_student():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Search query required'}), 400

    # Find participant
    participants = query("""
        SELECT * FROM participants
        WHERE name ILIKE %s OR email ILIKE %s
    """, (f'%{q}%', f'%{q}%'))

    if not participants:
        return jsonify([])

    result = []
    for p in participants:
        # Get their registrations with event details
        regs = query("""
            SELECT r.registration_id, e.event_name, e.date, e.venue
            FROM registrations r
            JOIN events e ON r.event_id = e.event_id
            WHERE r.participant_id = %s
        """, (p['participant_id'],))

        # Get their results
        results = query("""
            SELECT res.position, res.award, e.event_name
            FROM results res
            JOIN registrations r ON res.registration_id = r.registration_id
            JOIN events e ON r.event_id = e.event_id
            WHERE r.participant_id = %s
        """, (p['participant_id'],))

        result.append({
            'participant': p,
            'registrations': regs,
            'results': results
        })

    return jsonify(result)

# ─────────────────────────────────────────
if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
