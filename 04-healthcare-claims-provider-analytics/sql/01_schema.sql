-- Healthcare Claims & Provider Operations Analytics
-- PostgreSQL schema for a simplified reporting-oriented star model.

DROP TABLE IF EXISTS fact_claims;
DROP TABLE IF EXISTS dim_provider;
DROP TABLE IF EXISTS dim_patient;

CREATE TABLE dim_patient (
    patient_id VARCHAR(20) PRIMARY KEY,
    age_band VARCHAR(20) NOT NULL,
    gender VARCHAR(30),
    state CHAR(2),
    chronic_condition_flag SMALLINT CHECK (chronic_condition_flag IN (0, 1))
);

CREATE TABLE dim_provider (
    provider_id VARCHAR(20) PRIMARY KEY,
    specialty VARCHAR(100) NOT NULL,
    facility_type VARCHAR(100) NOT NULL,
    state CHAR(2)
);

CREATE TABLE fact_claims (
    claim_id VARCHAR(20),
    patient_id VARCHAR(20),
    provider_id VARCHAR(20),
    service_date DATE NOT NULL,
    encounter_type VARCHAR(30) NOT NULL,
    diagnosis_category VARCHAR(100),
    payer_type VARCHAR(30) NOT NULL,
    claim_status VARCHAR(20) NOT NULL,
    submitted_amount NUMERIC(14,2),
    allowed_amount NUMERIC(14,2),
    paid_amount NUMERIC(14,2),
    processing_days INTEGER,
    denial_reason VARCHAR(100),
    length_of_stay_days INTEGER,
    readmission_30d_flag SMALLINT
);

-- In a production pipeline, load raw data into a staging table first.
-- The synthetic project intentionally contains a few exceptions so they can
-- be detected before clean dimensional/fact loading or dashboard reporting.
