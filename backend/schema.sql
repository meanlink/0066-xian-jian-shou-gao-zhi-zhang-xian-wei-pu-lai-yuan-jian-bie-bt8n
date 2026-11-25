CREATE TABLE IF NOT EXISTS paper_cases (
 code text PRIMARY KEY, shelf text NOT NULL, title text NOT NULL,
 phase text NOT NULL CHECK(phase IN ('intake','imaged','filed')),
 requested_on date NOT NULL
);
CREATE TABLE IF NOT EXISTS paper_references (
 code text PRIMARY KEY, batch text NOT NULL, source text NOT NULL,
 rag int NOT NULL CHECK(rag BETWEEN 0 AND 100), reed int NOT NULL CHECK(reed BETWEEN 0 AND 100),
 bast int NOT NULL CHECK(bast BETWEEN 0 AND 100), pore int NOT NULL CHECK(pore BETWEEN 0 AND 100),
 accepted boolean NOT NULL
);
-- The legacy table kept only one mutable row per case. Comparisons are derived,
-- recomputable data, so discard the old shape before recreating the versioned one.
DO $$
BEGIN
 IF EXISTS (SELECT 1 FROM information_schema.tables
            WHERE table_schema='public' AND table_name='spectrum_matches')
    AND NOT EXISTS (SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='spectrum_matches'
              AND column_name='reference_snapshot') THEN
  DROP TABLE spectrum_matches;
 END IF;
END $$;
-- Monotonic clock for reference-bank membership. Any change advances it, so a
-- comparison is invalidated permanently even if the bank is later restored to
-- its previous appearance.
CREATE TABLE IF NOT EXISTS reference_clock (
 singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),
 epoch bigint NOT NULL DEFAULT 0 CHECK(epoch >= 0),
 changed_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO reference_clock(singleton) VALUES (true) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS paper_impressions (
 case_code text REFERENCES paper_cases(code), revision int CHECK(revision>0),
 rag int NOT NULL CHECK(rag BETWEEN 0 AND 100), reed int NOT NULL CHECK(reed BETWEEN 0 AND 100),
 bast int NOT NULL CHECK(bast BETWEEN 0 AND 100), pore int NOT NULL CHECK(pore BETWEEN 0 AND 100),
 slide text NOT NULL UNIQUE, PRIMARY KEY(case_code,revision)
);
-- Every comparison is its own immutable record. `id` is assigned in queue order
-- (under the advisory lock), so the newest *queued* comparison stays current even
-- if an older task finishes later. `revision` and `reference_epoch`, plus the
-- frozen reference snapshot, are captured at queue time; validity is judged
-- against the live clock and the latest revision.
CREATE TABLE IF NOT EXISTS spectrum_matches (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 case_code text NOT NULL REFERENCES paper_cases(code), job_id bigint,
 revision int NOT NULL, reference_epoch bigint NOT NULL,
 features text[] NOT NULL, reference_snapshot jsonb NOT NULL,
 status text NOT NULL DEFAULT 'pending'
  CHECK (status IN ('pending','ready','failed')),
 similarities jsonb, winner text,
 margin real CHECK(margin>=0), validation real CHECK(validation BETWEEN 0 AND 1),
 error text, queued_at timestamptz NOT NULL DEFAULT now(), computed_at timestamptz,
 FOREIGN KEY(case_code,revision) REFERENCES paper_impressions(case_code,revision)
);
CREATE INDEX IF NOT EXISTS spectrum_matches_case ON spectrum_matches(case_code,id);
CREATE TABLE IF NOT EXISTS shelf_returns (
 case_code text PRIMARY KEY REFERENCES paper_cases(code), revision int NOT NULL,
 finding text NOT NULL, shelf text NOT NULL, reviewer text NOT NULL, caveat text NOT NULL,
 filed_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(case_code,revision) REFERENCES paper_impressions(case_code,revision)
);
-- Pin the signed comparison; legacy receipts (and legacy tables) get NULL here.
ALTER TABLE shelf_returns ADD COLUMN IF NOT EXISTS match_id bigint REFERENCES spectrum_matches(id);
