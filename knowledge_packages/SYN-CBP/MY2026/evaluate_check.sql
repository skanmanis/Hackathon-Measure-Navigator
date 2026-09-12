-- ============================================================================
-- EVALUATE_CHECK — SYNTHETIC PROTOTYPE, FACT-DRIVEN (no member data required)
-- Replaces the earlier member-table-driven SP_CALCULATE_CBP_MEASURE approach
-- for the hackathon: this service only ever touches (a) the reference
-- VALUE_SET table (public code systems, synthetic groupings — same as before)
-- and (b) a small JSON bundle of scenario facts the user supplies in-session.
-- No member, claim, or enrollment table is read or required.
-- ============================================================================

USE SCHEMA HEDIS_SANDBOX.CBP_DEMO;

-- ---------------------------------------------------------------------------
-- CHECK_CATALOG: mirrors check_catalog.json — the "what to ask" layer.
-- The app can query this table directly, or ship the JSON twin with the app
-- so it doesn't need a DB round-trip just to know what to ask.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE TABLE CHECK_CATALOG (
    CHECK_ID        VARCHAR(40)  NOT NULL PRIMARY KEY,
    SUPPORTS_RULE   VARCHAR(80),
    QUESTION        VARCHAR(300),
    VALUE_SET_OID   VARCHAR(30),
    LOGIC_SUMMARY   VARCHAR(300)
);

INSERT INTO CHECK_CATALOG (CHECK_ID, SUPPORTS_RULE, QUESTION, VALUE_SET_OID, LOGIC_SUMMARY) VALUES
('CHK-HTN-DX-VALID',        'HTN-DX-1 / HTN-DX-2',              'Is this diagnosis code a qualifying hypertension diagnosis?',            'SYN.CBP.VS.001', 'diagnosis_code in value set'),
('CHK-DATE-BY-JUN30',       'HTN-DX-1',                          'Is this service date on/before June 30 of the measurement year?',        NULL,             'service_date <= MY-06-30'),
('CHK-DATE-BY-YEAREND',     'HTN-DX-2 / exclusions / numerator', 'Is this date on/before December 31 of the measurement year?',            NULL,             'the_date <= MY-12-31'),
('CHK-ESRD-DX',             'EXCL-ESRD-DX',                      'Is this diagnosis code an ESRD diagnosis?',                               'SYN.CBP.VS.004', 'diagnosis_code in value set'),
('CHK-ESRD-PX',             'EXCL-ESRD-PX',                      'Is this procedure code a dialysis/transplant/nephrectomy procedure?',    'SYN.CBP.VS.005', 'procedure_code in value set'),
('CHK-PREGNANCY-DX',        'EXCL-PREGNANCY',                    'Is this diagnosis a pregnancy diagnosis?',                                'SYN.CBP.VS.006', 'diagnosis_code in value set'),
('CHK-HOSPICE',             'EXCL-HOSPICE',                      'Does this line indicate hospice care?',                                   'SYN.CBP.VS.007', 'code in value set'),
('CHK-NONACUTE-POS',        'EXCL-NONACUTE-INPT',                'Is this a non-acute inpatient place of service?',                         'SYN.CBP.VS.014', 'pos_code in value set'),
('CHK-FRAILTY-DX',          'EXCL-FRAILTY-ADVANCED-ILLNESS',     'Is this diagnosis a frailty indicator?',                                  'SYN.CBP.VS.008', 'diagnosis_code in value set'),
('CHK-ADVANCED-ILLNESS-DX', 'EXCL-FRAILTY-ADVANCED-ILLNESS',     'Is this diagnosis an advanced illness indicator?',                        'SYN.CBP.VS.009', 'diagnosis_code in value set'),
('CHK-READING-DATE-VALID',  'numerator selection_rule',          'Was the reading taken on/after the second qualifying HTN diagnosis?',    NULL,             'reading_date >= second_dx_date'),
('CHK-READING-SETTING',     'numerator excluded_sources',        'Was the reading taken during acute inpatient or ED?',                    'SYN.CBP.VS.015', 'pos_code in value set -> excludes reading'),
('CHK-READING-MODIFIER',    'numerator excluded_sources',        'Does the CPT Cat II code carry an exception modifier?',                   'SYN.CBP.VS.013', 'modifier in value set -> excludes reading'),
('CHK-BP-CONTROLLED',       'numerator rate_definition',         'Is systolic < 140 AND diastolic < 90?',                                   NULL,             'systolic < 140 AND diastolic < 90');

-- ---------------------------------------------------------------------------
-- Generic helper: is a code a member of a value set? (reference-data lookup
-- only — same VALUE_SET table from the earlier synthetic VSD, no member data)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION FN_CODE_IN_VALUE_SET(P_VALUE_SET_OID VARCHAR, P_CODE_SYSTEM VARCHAR, P_CODE VARCHAR)
RETURNS BOOLEAN
AS
$$
    EXISTS (
        SELECT 1 FROM VALUE_SET
        WHERE VALUE_SET_OID = P_VALUE_SET_OID
          AND UPPER(CODE_SYSTEM) = UPPER(P_CODE_SYSTEM)
          AND UPPER(CODE) = UPPER(P_CODE)
    )
$$;

-- ---------------------------------------------------------------------------
-- EVALUATE_CHECK: the core of the guided interview.
-- Input:  CHECK_ID, and a small JSON object of ONLY the facts that check
--         needs (e.g. '{"diagnosis_code":"N18.6","code_system":"ICD-10-CM"}')
-- Output: VARIANT — {status, explanation, missing_facts, value_set_oid}
--   status = 'MET' | 'NOT_MET' | 'NEEDS_MORE_INFO' | 'UNKNOWN_CHECK'
-- No member, claim, or enrollment table is touched anywhere in this procedure.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE EVALUATE_CHECK(P_CHECK_ID VARCHAR, P_FACTS_JSON VARCHAR)
RETURNS VARIANT
LANGUAGE SQL
AS
$$
DECLARE
    facts        VARIANT;
    vs_oid       VARCHAR;
    result_bool  BOOLEAN;
    missing      ARRAY DEFAULT ARRAY_CONSTRUCT();
    unknown_keys ARRAY DEFAULT ARRAY_CONSTRUCT();
BEGIN
    facts := PARSE_JSON(P_FACTS_JSON);

    -- -----------------------------------------------------------------
    -- Generic "explicitly unknown" handling, ahead of any check-specific
    -- logic below. A fact value of the literal string "UNKNOWN" means the
    -- user was asked and doesn't have it -- this is NOT the same as a
    -- missing/not-yet-asked fact. It is captured as an open condition:
    -- both outcomes get stated, and the caller is expected to keep
    -- evaluating every OTHER check rather than stopping here. This is
    -- the mechanism that guarantees "I don't know" never reads as a
    -- refusal to proceed.
    -- -----------------------------------------------------------------
    FOR rec IN (SELECT KEY, VALUE FROM TABLE(FLATTEN(INPUT => facts))) DO
        IF (UPPER(rec.value::VARCHAR) = 'UNKNOWN') THEN
            unknown_keys := ARRAY_APPEND(unknown_keys, rec.key);
        END IF;
    END FOR;
    IF (ARRAY_SIZE(unknown_keys) > 0) THEN
        RETURN OBJECT_CONSTRUCT(
            'status', 'OPEN_CONDITION',
            'check_id', P_CHECK_ID,
            'unknown_facts', unknown_keys,
            'explanation', 'This fact is explicitly unknown, not just unanswered yet. Treat as an open condition: state both possible outcomes conditionally in the final answer, and continue evaluating every other relevant check -- this does not block or end the investigation. See check_catalog.json -> if_unknown for this check''s specific dual-outcome wording.'
        );
    END IF;

    CASE (P_CHECK_ID)

        WHEN 'CHK-HTN-DX-VALID' THEN
            IF (facts:diagnosis_code IS NULL) THEN missing := ARRAY_APPEND(missing, 'diagnosis_code'); END IF;
            IF (facts:code_system  IS NULL) THEN missing := ARRAY_APPEND(missing, 'code_system'); END IF;
            IF (ARRAY_SIZE(missing) > 0) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',missing);
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.001', facts:code_system::VARCHAR, facts:diagnosis_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT(
                'status', IFF(result_bool, 'MET', 'NOT_MET'),
                'value_set_oid', 'SYN.CBP.VS.001',
                'explanation', IFF(result_bool,
                    'Diagnosis code is in the Essential Hypertension value set.',
                    'Diagnosis code is NOT in the Essential Hypertension value set.')
            );

        WHEN 'CHK-ESRD-DX' THEN
            IF (facts:diagnosis_code IS NULL OR facts:code_system IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('diagnosis_code','code_system'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.004', facts:code_system::VARCHAR, facts:diagnosis_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT(
                'status', IFF(result_bool, 'MET', 'NOT_MET'),
                'value_set_oid', 'SYN.CBP.VS.004',
                'explanation', IFF(result_bool,
                    'This diagnosis IS an ESRD code -> triggers EXCL-ESRD-DX (member would be excluded from the denominator).',
                    'This diagnosis is not in the ESRD value set -> does not trigger this exclusion.')
            );

        WHEN 'CHK-ESRD-PX' THEN
            IF (facts:procedure_code IS NULL OR facts:code_system IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('procedure_code','code_system'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.005', facts:code_system::VARCHAR, facts:procedure_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT(
                'status', IFF(result_bool, 'MET', 'NOT_MET'),
                'value_set_oid', 'SYN.CBP.VS.005',
                'explanation', IFF(result_bool,
                    'This procedure IS an ESRD-indicating procedure (dialysis/transplant/nephrectomy) -> triggers EXCL-ESRD-PX.',
                    'This procedure is not in the ESRD procedure value set -> does not trigger this exclusion.')
            );

        WHEN 'CHK-PREGNANCY-DX' THEN
            IF (facts:diagnosis_code IS NULL OR facts:code_system IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('diagnosis_code','code_system'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.006', facts:code_system::VARCHAR, facts:diagnosis_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT(
                'status', IFF(result_bool, 'MET', 'NOT_MET'),
                'value_set_oid', 'SYN.CBP.VS.006',
                'explanation', IFF(result_bool,
                    'This diagnosis IS a pregnancy code -> triggers EXCL-PREGNANCY.',
                    'This diagnosis is not in the pregnancy value set -> does not trigger this exclusion.')
            );

        WHEN 'CHK-HOSPICE' THEN
            IF (facts:procedure_or_pos_code IS NULL OR facts:code_system IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('procedure_or_pos_code','code_system'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.007', facts:code_system::VARCHAR, facts:procedure_or_pos_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT(
                'status', IFF(result_bool, 'MET', 'NOT_MET'),
                'value_set_oid', 'SYN.CBP.VS.007',
                'explanation', IFF(result_bool,
                    'This code IS a hospice indicator -> triggers EXCL-HOSPICE.',
                    'This code is not in the hospice value set -> does not trigger this exclusion.')
            );

        WHEN 'CHK-NONACUTE-POS' THEN
            IF (facts:pos_code IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('pos_code'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.014', 'POS', facts:pos_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT(
                'status', IFF(result_bool, 'MET', 'NOT_MET'),
                'value_set_oid', 'SYN.CBP.VS.014',
                'explanation', IFF(result_bool,
                    'This place of service IS non-acute inpatient -> triggers EXCL-NONACUTE-INPT.',
                    'This place of service is not in the non-acute inpatient value set.')
            );

        WHEN 'CHK-FRAILTY-DX' THEN
            IF (facts:diagnosis_code IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('diagnosis_code'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.008', 'ICD-10-CM', facts:diagnosis_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT('status', IFF(result_bool,'MET','NOT_MET'), 'value_set_oid','SYN.CBP.VS.008',
                'explanation', IFF(result_bool, 'This diagnosis IS a frailty indicator.', 'This diagnosis is not a frailty indicator.'));

        WHEN 'CHK-ADVANCED-ILLNESS-DX' THEN
            IF (facts:diagnosis_code IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('diagnosis_code'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.009', 'ICD-10-CM', facts:diagnosis_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT('status', IFF(result_bool,'MET','NOT_MET'), 'value_set_oid','SYN.CBP.VS.009',
                'explanation', IFF(result_bool, 'This diagnosis IS an advanced illness indicator.', 'This diagnosis is not an advanced illness indicator.'));
            -- Note: EXCL-FRAILTY-ADVANCED-ILLNESS requires BOTH CHK-FRAILTY-DX and
            -- CHK-ADVANCED-ILLNESS-DX (plus age 66+) to be MET -- the app combines
            -- the two check results rather than this being a single check.

        WHEN 'CHK-READING-DATE-VALID' THEN
            IF (facts:reading_date IS NULL OR facts:second_dx_date IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('reading_date','second_dx_date'));
            END IF;
            result_bool := (TO_DATE(facts:reading_date::VARCHAR) >= TO_DATE(facts:second_dx_date::VARCHAR));
            RETURN OBJECT_CONSTRUCT('status', IFF(result_bool,'MET','NOT_MET'),
                'explanation', IFF(result_bool,
                    'Reading date is on/after the second qualifying HTN diagnosis -> eligible to be the representative reading.',
                    'Reading date is BEFORE the second qualifying HTN diagnosis -> cannot be used as the representative reading.'));

        WHEN 'CHK-READING-SETTING' THEN
            IF (facts:pos_code IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('pos_code'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.015', 'POS', facts:pos_code::VARCHAR);
            RETURN OBJECT_CONSTRUCT('status', IFF(result_bool,'NOT_MET','MET'), 'value_set_oid','SYN.CBP.VS.015',
                -- NOTE: for this check, finding the code IN the value set means the
                -- reading is EXCLUDED (inpatient/ED), so 'MET' = "usable as numerator evidence"
                'explanation', IFF(result_bool,
                    'Reading was taken during acute inpatient or ED -> this reading CANNOT be used for the numerator.',
                    'Reading setting is not inpatient/ED -> this reading is usable for the numerator (pending other checks).'));

        WHEN 'CHK-READING-MODIFIER' THEN
            IF (facts:cpt_ii_modifier IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('cpt_ii_modifier'));
            END IF;
            result_bool := FN_CODE_IN_VALUE_SET('SYN.CBP.VS.013', 'MODIFIER', facts:cpt_ii_modifier::VARCHAR);
            RETURN OBJECT_CONSTRUCT('status', IFF(result_bool,'NOT_MET','MET'), 'value_set_oid','SYN.CBP.VS.013',
                'explanation', IFF(result_bool,
                    'Modifier is an exception modifier (1P/2P/8P) -> this reading CANNOT be used for the numerator.',
                    'No exclusion modifier present -> this reading is usable for the numerator (pending other checks).'));

        WHEN 'CHK-BP-CONTROLLED' THEN
            IF (facts:systolic IS NULL OR facts:diastolic IS NULL) THEN
                RETURN OBJECT_CONSTRUCT('status','NEEDS_MORE_INFO','missing_facts',ARRAY_CONSTRUCT('systolic','diastolic'));
            END IF;
            result_bool := (facts:systolic::NUMBER < 140 AND facts:diastolic::NUMBER < 90);
            RETURN OBJECT_CONSTRUCT('status', IFF(result_bool,'MET','NOT_MET'),
                'explanation', IFF(result_bool,
                    'Systolic < 140 AND diastolic < 90 -> numerator compliant.',
                    'Reading does not meet the <140/<90 threshold -> numerator NOT compliant.'));

        ELSE
            RETURN OBJECT_CONSTRUCT('status', 'UNKNOWN_CHECK', 'explanation', 'No check defined for this check_id.');
    END CASE;
END;
$$;

-- ============================================================================
-- Usage examples (no member table involved anywhere):
--
--   CALL EVALUATE_CHECK('CHK-ESRD-DX', '{"diagnosis_code":"N18.6","code_system":"ICD-10-CM"}');
--   -> {"status":"MET","value_set_oid":"SYN.CBP.VS.004","explanation":"This diagnosis IS an ESRD code -> triggers EXCL-ESRD-DX ..."}
--
--   CALL EVALUATE_CHECK('CHK-READING-SETTING', '{"pos_code":"23"}');
--   -> {"status":"NOT_MET", ...}   -- meaning: reading was ED -> NOT usable for numerator
--
--   CALL EVALUATE_CHECK('CHK-BP-CONTROLLED', '{"systolic":138}');
--   -> {"status":"NEEDS_MORE_INFO","missing_facts":["diastolic"]}
--      -- the app should now ask the user for diastolic, not guess it.
--
--   -- THE "I don't know where the reading was taken" SCENARIO:
--   CALL EVALUATE_CHECK('CHK-READING-SETTING', '{"pos_code":"UNKNOWN"}');
--   -> {"status":"OPEN_CONDITION","unknown_facts":["pos_code"],
--       "explanation":"... state both possible outcomes conditionally ... continue evaluating every other relevant check ..."}
--      -- the app does NOT stop here. It proceeds to CHK-READING-MODIFIER and
--      -- CHK-BP-CONTROLLED with whatever facts ARE known, then composes one
--      -- answer: "readings <140/90 with the setting unconfirmed -- if it was
--      -- taken inpatient/ED it wouldn't count; otherwise the member is
--      -- numerator-compliant." That's a complete answer with one flagged gap,
--      -- not a refusal.
-- ============================================================================
