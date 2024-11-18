USE ROLE ACCOUNTADMIN;
USE WAREHOUSE cortex_analyst_wh;
SET (streamlit_warehouse)=(SELECT CURRENT_WAREHOUSE());

USE SCHEMA CORTEX_ANALYST_DEMO.REVENUE_TIMESERIES;

CREATE OR REPLACE STAGE STREAMLIT_STAGE DIRECTORY = (ENABLE = TRUE);

-- Upload 3rd party packages
-- Run from sis_setup/ as paths are relative to this directory


-- Upload App logic
PUT file://sis_setup/environment.yml @CORTEX_ANALYST_DEMO.REVENUE_TIMESERIES.STREAMLIT_STAGE/anslyst_demo/ OVERWRITE = TRUE AUTO_COMPRESS = FALSE;
PUT file://sis_setup/cortex_analyst_sis_demo_app.py @CORTEX_ANALYST_DEMO.REVENUE_TIMESERIES.STREAMLIT_STAGE/anslyst_demo/ OVERWRITE = TRUE AUTO_COMPRESS = FALSE;

-- Create Streamlit
CREATE OR REPLACE STREAMLIT CORTEX_ANALYST_DEMO.REVENUE_TIMESERIES.CORTEX_ANALYST_DEMO
ROOT_LOCATION = '@CORTEX_ANALYST_DEMO.REVENUE_TIMESERIES.STREAMLIT_STAGE/anslyst_demo'
MAIN_FILE = 'cortex_analyst_sis_demo_app.py'
TITLE = "Cortex Analyst"
QUERY_WAREHOUSE = $streamlit_warehouse
COMMENT = '{"origin": "sf_sit",
            "name": "skimantics",
            "version": {"major": 2, "minor": 0},
            "attributes": {"deployment": "sis"}}';