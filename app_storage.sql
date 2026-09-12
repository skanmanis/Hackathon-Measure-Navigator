PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS faqs (
  id INTEGER PRIMARY KEY, measure_id TEXT NOT NULL, measurement_year INTEGER NOT NULL,
  question TEXT NOT NULL, answer TEXT NOT NULL, keywords TEXT NOT NULL DEFAULT '',
  source_refs TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'approved',
  helpful_count INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY, masked_question TEXT NOT NULL, route TEXT, current_node TEXT,
  facts_json TEXT NOT NULL DEFAULT '{}', open_conditions_json TEXT NOT NULL DEFAULT '[]',
  outcome_state TEXT NOT NULL DEFAULT 'NO_CONFIRMATION', final_answer TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS interactions (
  id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), masked_input TEXT NOT NULL,
  stage TEXT NOT NULL, response_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS learning_records (
  id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
  state TEXT NOT NULL CHECK(state IN ('CONFIRMED_WORKED','CONFIRMED_UNRESOLVED','NO_CONFIRMATION','REVIEWED')),
  generalized_question TEXT, generalized_answer TEXT, reviewer_notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS escalations (
  id TEXT PRIMARY KEY, session_id TEXT REFERENCES sessions(id), severity TEXT NOT NULL,
  reason TEXT NOT NULL, authoritative_source TEXT NOT NULL DEFAULT 'SPECIFICATION',
  conflicting_source TEXT, status TEXT NOT NULL DEFAULT 'OPEN',
  assigned_queue TEXT NOT NULL DEFAULT 'MEASURE_REVIEW',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, resolved_at TEXT
);
