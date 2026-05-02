// OJAS 2K26 — Upcoming Events Seed Script
// Run this in your browser console OR as: node seed_events.js

const SUPA_URL = 'https://rinpqlroqxblsmjqcequ.supabase.co/rest/v1';
const KEY = 'sb_publishable_aEFZNFjFYQ21Eyxr3oORxQ_7Tdzz13F';

const headers = {
  'apikey': KEY,
  'Authorization': `Bearer ${KEY}`,
  'Content-Type': 'application/json',
  'Prefer': 'return=minimal'
};

const upcomingEvents = [
  {
    event_name: "Battle of Bands",
    date: "2026-05-05",
    time: "10:00 - 12:00 PM",
    venue: "Open Air Theatre",
    organizer_club: "Music Club",
    event_type: "Group 1",
    school: "School of Arts, Humanities & Social Sciences"
  },
  {
    event_name: "Stand-Up Comedy Night",
    date: "2026-05-05",
    time: "2:00 - 4:00 PM",
    venue: "Acad 1 Room 101",
    organizer_club: "Drama Club",
    event_type: "Solo",
    school: "School of Arts, Humanities & Social Sciences"
  },
  {
    event_name: "Hackathon 2K26",
    date: "2026-05-07",
    time: "9:00 AM - 6:00 PM",
    venue: "Computer Lab Block B",
    organizer_club: "Tech Club",
    event_type: "Group 2",
    school: "School of Engineering"
  },
  {
    event_name: "Debate Championship",
    date: "2026-05-07",
    time: "11:00 AM - 1:00 PM",
    venue: "Seminar Hall",
    organizer_club: "Debate Society",
    event_type: "Solo",
    school: "School of Law, Governance & Public Policy"
  },
  {
    event_name: "Photography Contest",
    date: "2026-05-08",
    time: "All Day",
    venue: "Campus Grounds",
    organizer_club: "Photography Club",
    event_type: "Solo",
    school: "School of Arts, Humanities & Social Sciences"
  },
  {
    event_name: "Startup Pitch",
    date: "2026-05-08",
    time: "3:00 - 5:00 PM",
    venue: "Preksha Auditorium",
    organizer_club: "E-Cell",
    event_type: "Group 1",
    school: "School of Management Sciences"
  },
  {
    event_name: "Classical Bharatanatyam",
    date: "2026-05-10",
    time: "5:00 - 7:00 PM",
    venue: "Preksha Auditorium",
    organizer_club: "Dance Club",
    event_type: "Solo",
    school: "School of Arts, Humanities & Social Sciences"
  },
  {
    event_name: "Sci-Fi Short Film",
    date: "2026-05-10",
    time: "2:00 - 4:00 PM",
    venue: "Room 205",
    organizer_club: "Film Society",
    event_type: "Group 2",
    school: "School of Engineering"
  },
  {
    event_name: "Math Olympiad",
    date: "2026-05-12",
    time: "10:00 AM - 12:00 PM",
    venue: "Exam Hall 3",
    organizer_club: "Math Club",
    event_type: "Solo",
    school: "School of Mathematics & Natural Sciences"
  },
  {
    event_name: "Bio Quiz Blitz",
    date: "2026-05-12",
    time: "2:00 - 3:30 PM",
    venue: "Lab Block A",
    organizer_club: "Bio Society",
    event_type: "Group 1",
    school: "School of Biosciences"
  },
];

async function seed() {
  console.log(`Seeding ${upcomingEvents.length} upcoming events into Supabase...`);
  let ok = 0, fail = 0;
  for (const ev of upcomingEvents) {
    const res = await fetch(`${SUPA_URL}/events`, {
      method: 'POST',
      headers,
      body: JSON.stringify(ev)
    });
    if (res.ok) {
      console.log(`✅ Added: ${ev.event_name}`);
      ok++;
    } else {
      const err = await res.text();
      console.log(`❌ Failed: ${ev.event_name} — ${err}`);
      fail++;
    }
  }
  console.log(`\nDone! ${ok} added, ${fail} failed.`);
}

seed();
