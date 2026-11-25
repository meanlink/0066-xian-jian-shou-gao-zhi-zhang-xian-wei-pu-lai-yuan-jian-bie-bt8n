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
CREATE TABLE IF NOT EXISTS paper_impressions (
 case_code text REFERENCES paper_cases(code), revision int CHECK(revision>0),
 rag int NOT NULL CHECK(rag BETWEEN 0 AND 100), reed int NOT NULL CHECK(reed BETWEEN 0 AND 100),
 bast int NOT NULL CHECK(bast BETWEEN 0 AND 100), pore int NOT NULL CHECK(pore BETWEEN 0 AND 100),
 slide text NOT NULL UNIQUE, PRIMARY KEY(case_code,revision)
);
CREATE TABLE IF NOT EXISTS spectrum_matches (
 case_code text PRIMARY KEY REFERENCES paper_cases(code), revision int NOT NULL,
 features text[] NOT NULL, similarities jsonb NOT NULL, winner text NOT NULL, margin real NOT NULL CHECK(margin>=0),
 validation real NOT NULL CHECK(validation BETWEEN 0 AND 1),
 FOREIGN KEY(case_code,revision) REFERENCES paper_impressions(case_code,revision)
);
CREATE TABLE IF NOT EXISTS shelf_returns (
 case_code text PRIMARY KEY REFERENCES paper_cases(code), revision int NOT NULL,
 finding text NOT NULL, shelf text NOT NULL, reviewer text NOT NULL, caveat text NOT NULL,
 filed_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(case_code,revision) REFERENCES paper_impressions(case_code,revision)
);
