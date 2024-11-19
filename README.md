# CORTEX ANALYST DEMO

This is a repository that inspired by Snowflake Cortex Analyst Tutorial

## Run locally

- create database objects and load data in [resources](./resources/) following [Tutorial](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/tutorials/tutorial-1#introduction) step 1-2 (step 3 may not work)
- rename .env.template to .env
- assign necessary variables in .env 
  (`SNOWFLAKE_HOST` and `PASSWORD_ENCRYPTED` are optional)
- run `streamlit run analyst_demo.py --server.port 8501`

## Deploy to Streamlit In Snowflake

- create database objects and load data in [resources](./resources/) following [Tutorial](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/tutorials/tutorial-1#introduction) step 1-2 (step 3 may not work)
- install Snowflake cli or SnowSql (following steps are for Snowflake cli)
- edit `~/.snowflake/connections.toml` to add new connection, for ref: [sis_setup/connections.toml.template](./sis_setup/connections.toml.template)
- run `snow sql -f ./sis_setup/app_setup.sql --connection sample_connection`
- run Streamlit app in Snowlight

## Questions

- [questions.txt](./questions.txt) shows sample questions