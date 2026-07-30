CREATE TABLE IF NOT EXISTS bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  team TEXT NOT NULL,
  captain TEXT NOT NULL,
  email TEXT NOT NULL,
  quiz_date TEXT NOT NULL,
  team_size INTEGER NOT NULL CHECK (team_size BETWEEN 1 AND 6),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (email, quiz_date)
);
CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings (quiz_date);
