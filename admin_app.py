import streamlit as st
import json
import pandas as pd
import datasets_list
import vertex_integration
import webflow_integration 
import re

# Initialize session state
if 'json_data' not in st.session_state:
    st.session_state.json_data = None

if 'selected_name' not in st.session_state:
    st.session_state.selected_name = "Please select"

if 'response_data' not in st.session_state:
    st.session_state.response_data = None

if 'generated_insights' not in st.session_state:
    st.session_state.generated_insights = ""

if 'visualization_url' not in st.session_state:
    st.session_state.visualization_url = ""

def reset_session():
    st.session_state.json_data = None
    st.session_state.selected_name = "Please select"
    st.session_state.response_data = None
    st.session_state.generated_insights = ""
    st.session_state.visualization_url = ""
    st.session_state.dataset_id = None

def display_json_data():
    if not st.session_state.json_data:
        st.error("No data available to display.")
        return

    json_data = st.session_state.json_data
    names_to_objects = {obj["name"]: obj for obj in json_data if "name" in obj}
    sorted_names = sorted(names_to_objects.keys())

    if not sorted_names:
        st.error("No 'name' keys found in the JSON data.")
        return

    try:
        dataframe = pd.DataFrame(json_data)
        st.write("### Table displaying JSON objects as rows:")
        st.dataframe(dataframe)
    except Exception as e:
        st.error(f"Error converting JSON data to a table: {e}")

    selected_name = st.selectbox(
        "Please select from one of the following datasets",
        options=["Please select"] + sorted_names,
        index=sorted_names.index(
            st.session_state.selected_name) + 1 if st.session_state.selected_name in sorted_names else 0
    )

    st.session_state.selected_name = selected_name

# Start of app code
st.title("This is the start of our AI journey zoom zoom bam bam")
st.write("Let's start building! Jeng Jeng")

if st.button("click me to view list of blobs in cloud storage"):
    try:
        st.session_state.json_data = datasets_list.download_blob()
        st.write("Data loaded")
    except Exception as e:
        st.error(f"Error loading data: {e}")

if st.session_state.json_data:
    display_json_data()

if st.session_state.selected_name != "Please select":
    st.write(f"You selected: {st.session_state.selected_name}")
    selected_object = {obj["name"]: obj for obj in st.session_state.json_data}.get(st.session_state.selected_name)
    if selected_object:
        if st.button("Generate content for selected dataset"):
            try:
                dataset_id = selected_object['datasetId']
                st.session_state.dataset_id = selected_object['datasetId']
                st.write(f"Generating content for datasetID: {dataset_id}")

                try:
                    format = selected_object['format']
                    if format == 'XLSX':
                        st.session_state.response_data = vertex_integration.datagov_xlsx_request(st.session_state.dataset_id)
                    elif format == 'GEOJSON':
                        st.session_state.response_data = vertex_integration.datagov_geojson_request(st.session_state.dataset_id)
                    elif format == 'CSV':
                        st.session_state.response_data = vertex_integration.datagov_csv_request(st.session_state.dataset_id)
                    else:
                        st.error("Invalid format. Please select a valid format.")

                    if st.session_state.response_data is not None:
                        model_data = vertex_integration.generate(st.session_state.response_data, st.session_state.dataset_id)
                        st.session_state.generated_insights = "".join(data.text for data in model_data)

                except Exception as e:
                    st.error(f"Error generating content: {e}")

            except Exception as e:
                st.error(f"Error generating content: {e}")

if st.session_state.generated_insights:
    st.write(st.session_state.generated_insights)
    
    if st.button("Generate Visualization"):
        if st.session_state.response_data:
            selected_object = {obj["name"]: obj for obj in st.session_state.json_data}.get(st.session_state.selected_name)
            if selected_object:
                dataset_id = selected_object['datasetId']
                try:
                    viz_data = vertex_integration.generate_visualisation(st.session_state.response_data, st.session_state.dataset_id)
                    st.session_state.visualization_url = "".join(data.text for data in viz_data)
                    st.write(st.session_state.visualization_url)
                except Exception as e:
                    st.error(f"Error generating visualization: {e}")

if st.session_state.visualization_url:
    if st.button("Publish to Webflow"):
        try:
            # Parse the generated insights into a dictionary
            start_index = st.session_state.generated_insights.find('{')
            end_index = st.session_state.generated_insights.rfind('}') + 1
            if start_index == -1 or end_index == -1:
                raise ValueError("JSON content not found in the insights.")
            
            json_string = st.session_state.generated_insights[start_index:end_index]

            field_data = json.loads(json_string)            # Add the visualization URL to the dictionary
            field_data['key-visualisation-link'] = st.session_state.visualization_url.strip()
            
            # Call the update_collection function
            response = webflow_integration.update_collection(field_data, st.session_state.dataset_id)
            st.success(response)
        except Exception as e:
            st.error(f"Error publishing to Webflow: {e}")

if st.button("Reset"):
    reset_session()



