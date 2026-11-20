-- Star schema for the UK carbon intensity pipeline.
-- Safe to run more than once (IF NOT EXISTS).

CREATE SCHEMA IF NOT EXISTS carbon;

-- Dimension: one row per UK region
CREATE TABLE IF NOT EXISTS carbon.dim_region (
    regionid   INT PRIMARY KEY,
    shortname  TEXT NOT NULL,
    dno        TEXT
);

-- Fact: daily average carbon intensity, partitioned by year
CREATE TABLE IF NOT EXISTS carbon.fact_carbon_intensity (
    regionid         INT  NOT NULL REFERENCES carbon.dim_region (regionid),
    date_recorded    DATE NOT NULL,
    intensity        NUMERIC(8, 2),
    intensity_index  TEXT,
    PRIMARY KEY (regionid, date_recorded)
) PARTITION BY RANGE (date_recorded);

CREATE TABLE IF NOT EXISTS carbon.fact_carbon_intensity_2026
    PARTITION OF carbon.fact_carbon_intensity
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Catches any date outside the yearly partitions, so loads never fail
CREATE TABLE IF NOT EXISTS carbon.fact_carbon_intensity_default
    PARTITION OF carbon.fact_carbon_intensity DEFAULT;

-- Fact: daily average generation mix (% by fuel). Missing from the old schema.
CREATE TABLE IF NOT EXISTS carbon.fact_generation_mix (
    regionid       INT  NOT NULL REFERENCES carbon.dim_region (regionid),
    date_recorded  DATE NOT NULL,
    biomass  NUMERIC(5, 2),
    coal     NUMERIC(5, 2),
    imports  NUMERIC(5, 2),
    gas      NUMERIC(5, 2),
    nuclear  NUMERIC(5, 2),
    other    NUMERIC(5, 2),
    hydro    NUMERIC(5, 2),
    solar    NUMERIC(5, 2),
    wind     NUMERIC(5, 2),
    PRIMARY KEY (regionid, date_recorded)
);

SELECT date_recorded, COUNT(*) FROM carbon.fact_carbon_intensity GROUP BY date_recorded;