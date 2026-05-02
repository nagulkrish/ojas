CREATE TABLE events (
  event_id      SERIAL PRIMARY KEY,
  event_name    TEXT NOT NULL,
  date          DATE,
  venue         TEXT,
  time          TEXT,
  organizer_club TEXT,
  event_type    TEXT,
  school        TEXT
);

CREATE TABLE participants (
  participant_id SERIAL PRIMARY KEY,
  name           TEXT NOT NULL,
  email          TEXT UNIQUE NOT NULL,
  phone          TEXT,
  school         TEXT
);

CREATE TABLE registrations (
  registration_id SERIAL PRIMARY KEY,
  event_id        INT REFERENCES events(event_id),
  participant_id  INT REFERENCES participants(participant_id),
  UNIQUE(event_id, participant_id)
);

CREATE TABLE results (
  result_id       SERIAL PRIMARY KEY,
  registration_id INT REFERENCES registrations(registration_id),
  winner_name     TEXT,
  position        TEXT,
  award           TEXT
);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE registrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read events" ON events FOR SELECT USING (true);
CREATE POLICY "Public read participants" ON participants FOR SELECT USING (true);
CREATE POLICY "Public read registrations" ON registrations FOR SELECT USING (true);
CREATE POLICY "Public read results" ON results FOR SELECT USING (true);

CREATE POLICY "Public insert events" ON events FOR INSERT WITH CHECK (true);
CREATE POLICY "Public insert participants" ON participants FOR INSERT WITH CHECK (true);

ALTER TABLE events DISABLE ROW LEVEL SECURITY;
ALTER TABLE participants DISABLE ROW LEVEL SECURITY;
ALTER TABLE registrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE results DISABLE ROW LEVEL SECURITY;

ALTER TABLE events DISABLE ROW LEVEL SECURITY;
ALTER TABLE participants DISABLE ROW LEVEL SECURITY;
ALTER TABLE registrations DISABLE ROW LEVEL SECURITY;
ALTER TABLE results DISABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS registration_requests (
  request_id    BIGSERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  email         TEXT NOT NULL,
  phone         TEXT,
  school        TEXT,
  event_id      BIGINT REFERENCES events(event_id) ON DELETE CASCADE,
  event_name    TEXT,            -- denormalized for easy display
  status        TEXT NOT NULL DEFAULT 'pending',  -- 'pending' | 'approved' | 'denied'
  submitted_at  TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at   TIMESTAMPTZ
);

ALTER TABLE registration_requests ENABLE ROW LEVEL SECURITY;

-- Policy: anyone can insert a new request
CREATE POLICY "Allow public insert" ON registration_requests
  FOR INSERT WITH CHECK (true);

-- Policy: anyone can read requests (needed for student status check by email)
CREATE POLICY "Allow public read" ON registration_requests
  FOR SELECT USING (true);

-- Policy: anyone can update status (admin uses publishable key; add auth check if you set up Supabase Auth)
CREATE POLICY "Allow public update" ON registration_requests
  FOR UPDATE USING (true);