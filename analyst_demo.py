from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import snowflake.connector
import streamlit as st
from streamlit_option_menu import option_menu

import settings

DATABASE = "CORTEX_ANALYST_DEMO"
SCHEMA = "REVENUE_TIMESERIES"
STAGE = "RAW_DATA"
# FILE = "revenue_timeseries.yaml"
# FILE = "revenue_timeseries_nosample.yaml"
# FILE = "revenue_timeseries_search_nosample.yaml"
# FILE = "revenue_timeseries_plus.yaml"
# FILE = "revenue_timeseries_noqueries.yaml"
FILE_TEMPLATRE = "revenue_timeseries_{}.yaml"
WAREHOUSE = "cortex_analyst_wh"

# replace values below with your Snowflake connection information
SNOWFLAKE_HOST = settings.SNOWFLAKE_HOST
ACCOUNT = settings.ACCOUNT
USER = settings.USER
PASSWORD = settings.PASSWORD
ROLE = settings.ROLE

if "CONN" not in st.session_state or st.session_state.CONN is None:
    st.session_state.CONN = snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        role=ROLE,
        database=DATABASE,
        schema=SCHEMA,
        host=SNOWFLAKE_HOST,
        port=443,
    )


def on_change(key: str) -> None:
    selection = st.session_state[key]
    if selection == "sharing":
        model_file = "sharing_tables.yaml"
    else:
        model_file = FILE_TEMPLATRE.format(selection)
    st.session_state.model_file = model_file


def send_message(prompt: str) -> Dict[str, Any]:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{st.session_state.model_file}",
    }
    # url = f"https://{st.session_state.CONN.host}/api/v2/cortex/analyst/message"
    url = f"https://{SNOWFLAKE_HOST}/api/v2/cortex/analyst/message"
    resp = requests.post(
        url=url,
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{st.session_state.CONN.rest.token}"',
            "Content-Type": "application/json",
        },
    )
    request_id = resp.headers.get("X-Snowflake-Request-Id")
    if resp.status_code < 400:
        return {**resp.json(), "request_id": request_id}  # type: ignore[arg-type]
    else:
        raise Exception(
            f"Failed request (id: {request_id}) with status {resp.status_code}: {resp.text}"
        )


def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            request_id = response["request_id"]
            content = response["message"]["content"]
            display_content(content=content, request_id=request_id)  # type: ignore[arg-type]
    st.session_state.messages.append(
        {"role": "assistant", "content": content, "request_id": request_id}
    )


def display_content(
    content: List[Dict[str, str]],
    request_id: Optional[str] = None,
    message_index: Optional[int] = None,
) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    if request_id:
        with st.expander("Request ID", expanded=False):
            st.markdown(request_id)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Running SQL..."):
                    df = pd.read_sql(item["statement"], st.session_state.CONN)
                    if len(df.index) > 1:
                        data_tab, line_tab, bar_tab = st.tabs(
                            ["Data", "Line Chart", "Bar Chart"]
                        )
                        data_tab.dataframe(df)
                        if len(df.columns) > 1:
                            df = df.set_index(df.columns[0])
                        with line_tab:
                            st.line_chart(df.iloc[:100, :1])
                        with bar_tab:
                            st.bar_chart(df.iloc[:100, :1])
                    else:
                        st.dataframe(df)


st.title("Cortex Analyst")
# st.markdown("Select a semantic model file to use:")
selected = option_menu("Select a semantic model file to use:",
    options=["default", "nosample", "search", "plus", "noqueries", "auto", "sharing"],
    menu_icon="cast", default_index=2, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffffaa"},
        "icon": {"color": "#ff0000", "font-size": "10px"},
        "nav-link": {"font-size": "10px", "text-align": "left", "margin": "0px", "--hover-color": "#fcf"},
        "nav-link-selected": {"background-color": "#ffaaff"},
    },
    on_change=on_change, key="model"
)

if "model_file" not in st.session_state:
    st.session_state.model_file = ""
st.markdown(f"Semantic Model: `{st.session_state.model_file}`")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None

for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        display_content(
            content=message["content"],
            request_id=message.get("request_id"),
            message_index=message_index,
        )

if user_input := st.chat_input("What is your question?"):
    process_message(prompt=user_input)

if st.session_state.active_suggestion:
    process_message(prompt=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None
