-- Complete SQL script to fix all boolean fields in customer_result, customer_mseb, and customer_inspectiondetail tables
-- Run this directly on your PostgreSQL database

-- Fix customer_result table boolean fields
DO $$
BEGIN
    -- Fix solar_panel
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'solar_panel'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN solar_panel TYPE boolean 
        USING CASE 
            WHEN solar_panel::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN solar_panel::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
    
    -- Fix inverter
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'inverter'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN inverter TYPE boolean 
        USING CASE 
            WHEN inverter::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN inverter::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
    
    -- Fix net_meter
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'net_meter'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN net_meter TYPE boolean 
        USING CASE 
            WHEN net_meter::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN net_meter::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
    
    -- Fix mseb
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'mseb'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN mseb TYPE boolean 
        USING CASE 
            WHEN mseb::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN mseb::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
    
    -- Fix solar_pump
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'solar_pump'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN solar_pump TYPE boolean 
        USING CASE 
            WHEN solar_pump::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN solar_pump::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
    
    -- Fix controller
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'controller'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN controller TYPE boolean 
        USING CASE 
            WHEN controller::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN controller::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
    
    -- Fix inspection_report
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
        AND table_name = 'customer_result' 
        AND column_name = 'inspection_report'
        AND data_type != 'boolean'
    ) THEN
        ALTER TABLE customer_result 
        ALTER COLUMN inspection_report TYPE boolean 
        USING CASE 
            WHEN inspection_report::text IN ('1', 'true', 't', 'TRUE', 'T', 'True') THEN true
            WHEN inspection_report::text IN ('0', 'false', 'f', 'FALSE', 'F', 'False', '') THEN false
            ELSE false
        END;
    END IF;
END $$;

-- Fix customer_mseb table boolean fields
DO $$
DECLARE
    col_name text;
    bool_cols text[] := ARRAY[
        'load_extension', 'flisibility', 'quotation', 'sent_to_bill',
        'net_meter', 'flexibility', 'approval', 'meter_testing',
        'agreement', 'release', 'installation_date'
    ];
BEGIN
    FOREACH col_name IN ARRAY bool_cols
    LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public'
            AND table_name = 'customer_mseb' 
            AND column_name = col_name
            AND data_type != 'boolean'
        ) THEN
            EXECUTE format('
                ALTER TABLE customer_mseb 
                ALTER COLUMN %I TYPE boolean 
                USING CASE 
                    WHEN %I::text IN (''1'', ''true'', ''t'', ''TRUE'', ''T'', ''True'') THEN true
                    WHEN %I::text IN (''0'', ''false'', ''f'', ''FALSE'', ''F'', ''False'', '''') THEN false
                    ELSE false
                END;
            ', col_name, col_name, col_name);
        END IF;
    END LOOP;
END $$;

-- Fix customer_inspectiondetail table boolean fields
DO $$
DECLARE
    col_name text;
    bool_cols text[] := ARRAY[
        'solar_module_completed', 'inverter_completed', 'net_meter_completed',
        'ct_completed', 'generation_meters_completed', 'gen_ct_meters_completed',
        'ac_panel_cabling_completed', 'dc_panel_cabling_completed',
        'fabrication_completed', 'walkway_completed', 'pipeline_completed',
        'ropeway_completed', 'rolling_completed', 'info_correct'
    ];
BEGIN
    FOREACH col_name IN ARRAY bool_cols
    LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public'
            AND table_name = 'customer_inspectiondetail' 
            AND column_name = col_name
            AND data_type != 'boolean'
        ) THEN
            EXECUTE format('
                ALTER TABLE customer_inspectiondetail 
                ALTER COLUMN %I TYPE boolean 
                USING CASE 
                    WHEN %I::text IN (''1'', ''true'', ''t'', ''TRUE'', ''T'', ''True'') THEN true
                    WHEN %I::text IN (''0'', ''false'', ''f'', ''FALSE'', ''F'', ''False'', '''') THEN false
                    ELSE false
                END;
            ', col_name, col_name, col_name);
        END IF;
    END LOOP;
END $$;


