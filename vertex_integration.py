import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import json
from requests import Response
import requests
import pandas as pd
# import boto3
from io import BytesIO, StringIO

import os

     # Path where Docker secrets are mounted
secret_path = '/run/secrets/google_credentials'

if os.path.exists(secret_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = secret_path

vertexai.init(project='winged-keyword-441104-q1', location='us-central1')

model = GenerativeModel(
    "gemini-1.5-flash-002",
)

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]


def init_vertexai():
    vertexai.init(project="winged-keyword-441104-q1", location="us-central1")

def datagov_geojson_request(dataset_id):
    # dataset_id = "d_930e662ac7e141fe3fd2a6efa5216902"
    url = "https://api-open.data.gov.sg/v1/public/api/datasets/" + dataset_id + "/poll-download"

    response: Response = requests.get(url)
    json_data = response.json()
    if json_data['code'] != 0:
        print(json_data['errMsg'])
        exit(1)

    url = json_data['data']['url']
    response = requests.get(url)
    response_string = response.content.decode('utf-8')

    return response_string

def datagov_xlsx_request(dataset_id):

    url = "https://api-open.data.gov.sg/v1/public/api/datasets/" + dataset_id + "/poll-download"
    response = requests.get(url)
    json_data = response.json()
    if json_data['code'] != 0:
        print(json_data['errMsg'])
        exit(1)
    url = json_data['data']['url']
    response = requests.get(url)
    excel_data = pd.read_excel(BytesIO(response.content),engine='openpyxl',sheet_name=None)
    df_combined = pd.concat(excel_data.values(), ignore_index=True)
    str_data = df_combined.to_string()


    return str_data


def datagov_csv_request(dataset_id):
    # Generate the GET Request and return the response
    url = "https://data.gov.sg/api/action/datastore_search?resource_id=" + dataset_id

    response = requests.get(url)
    str_data = json.dumps(response.json())

    # Return the DataFrame as a string
    return str_data

def generate(document,dataset_id):
    global data_string
    init_vertexai()
    # vertexai.init(project="winged-keyword-441104-q1", location="us-central1")

    responses_kig = model.generate_content(
        ["""
I have a collection of datasets in various formats, including CSV, XSLX, GeoJson, KML and KMZ. These datasets may contain geospatial data, numerical data, or plain text. I need to generate key insights for reports that accurately represent the information in these datasets. The insights should be centered around noticing patterns, trends, and anomalies, and should provide a general sensing of the implications this data has on the way things are going. Additionally, the insights should include statistical summaries such as minimum, maximum, and average values where necessary. Here are the specific requirements:
Note, ignore any n/a values or missing values in your analysis but note that it can be limiting to the conclusions drawn. Also note that some datasets might contain headers like 20112 where the year is 2011 but 2 is a superscript. Ignore the last values. Only mention this as a footnote
CSV and XSLX Files:
Numerical Data:
Extract key insights, including:
Noticing patterns or trends. This is the key part of the analysis, providing these patterns in context also helps for people to understand what they are seeing.
Pointing out anomalies. Do this asa a note.
Providing a general sensing of the implications of the data.
Including statistical summaries such as minimum, maximum, and average values where necessary.
Text-heavy Data:
Treat these files as text files.
Provide a quick summary of key takeaways from the text data.
GeoJson, KML, and KMZ Files:
Geospatial Data:
Extract key insights, including:
Noticing patterns or trends.
Pointing out anomalies.
Providing a general sensing of the implications of the data.
Including statistical summaries such as minimum, maximum, and average values where necessary.
The dataset will be passed in as a string that has been processed as such:
 import json
# Example bytes data (replace this with your actual bytes data)
geojson_bytes = b'{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [102.0, 0.5]}, "properties": {"prop0": "value0"}}]}'


# Step 1: Decode bytes to string
geojson_str = geojson_bytes.decode('utf-8')


# Step 2: Load the JSON string into a Python dictionary
geojson_data = json.loads(geojson_str)


# Step 3: Convert the dictionary back to a formatted JSON string
formatted_geojson_str = json.dumps(geojson_data, indent=4)


# Print the formatted GeoJSON string
print(formatted_geojson_str)
Make sure to parse this information when performing analysis
Similar approaches are used for KML and KMZ files
Based on these strings, try to evaluate the closeness of coordinates and mention the associated area they are referring to. Take note of any large concentration of timestamps around specific areas if relevant for the analysis.
APIs:
JSON Data:
Parse the JSON data to extract relevant numerical or geospatial information.
Extract key insights, including:
Noticing patterns or trends.
Pointing out anomalies.
Providing a general sensing of the implications of the data.
Including statistical summaries such as minimum, maximum, and average values where necessary.
Other Data Formats:
Identify the data format and extract appropriate insights as per the above categories.
Example Requests:
For a CSV file containing sales data:
Extract key insights such as sales trends over time, any anomalies in sales data, and implications for future sales strategies. Include minimum, maximum, and average sales figures.
For a GeoJson file containing earthquake data:
Extract key insights such as patterns in earthquake occurrences, anomalies in earthquake data, and implications for disaster preparedness. Include minimum, maximum, and average earthquake intensities.
For an API returning JSON data on weather patterns:
Extract key insights such as trends in temperature changes, anomalies in weather patterns, and implications for climate change. Include minimum, maximum, and average temperature values.
For a CSV file with text data on customer feedback:
Provide a quick summary of key takeaways from the text data.
Format the output as a json file with
reporting-agency: the agency providing the dataset
data-source: a link to the data source
last-updated: the date in which the data was produced
name: the name of the report for the insights that had been generated 
slug: a url slug based on the name generated for this report e.g. “report-name”
data-source-name: name of the provider of the data source. Make it data.gov.sg
key-insight: a rich text format that will be rendered in Webflow in the following structure with each structure beginning with a H3 header text:
Key Insight as a single paragraph summarizing the major takeaways. Make sure to be specific about what you are trying to communicate to the reader. Imagine you are a news presenter providing insight to the state of affairs.
Small interesting points of note
Methodology for how you performed the analysis in point form. Try to speak a little bit as to how the data was prepared. But focus more on what the specific insight you derived was and the rationalizing of that information. Try to be as comprehensive as possible so others may understand how you drew these conclusions.
Add footnotes on things like the removal of the superscript and other processing information.
Ensure that the rich text format adds line breaks between sections to format it better. For Example, the Key Insight have a few empty lins before the points of note.
This json should be readable so that I can pass it to webflow collection API. do not change the variable names cited.
Example output: 
{
  "reporting-agency": "Ministry of Health",
  "data-source":"https://data.gov.sg/datasets/d_ac42b0ea4ae0528bc9dbef90f0658f2b/view",
  "last-updated": "2024-12-01",
  "name": "COVID-19 Cases in Singapore - December 2024",
  "slug": "covid-19-cases-in-singapore-december-2024",
  "data-source-name": "data.gov.sg",
  "key-insight": "<h3>Key Insight</h3><p>The number of COVID-19 cases in Singapore has shown a steady decline over the past month, indicating effective control measures.</p><h3>Small Interesting Points of Note</h3><p>There was a significant drop in cases among the younger population, possibly due to increased vaccination rates.</p><h3>Methodology</h3><ul><li>Aggregated daily case counts to weekly averages.</li><li>Removed outliers to ensure data consistency.</li><li>Analyzed trends using linear regression models.</li></ul><h3>Footnotes</h3><p>Superscript numbers and special characters were removed during data cleaning to ensure clarity.</p>"
}
Only ever give back the formatted JSON and only the JSON. This format MUST be enforced as the json will be used to parse data to another function. Note for the link, the d_ is a unique identifier for the appropriate dataset. Make sure that this is passed through

""", document,dataset_id],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    return responses_kig
    # for response in responses_kig:
    #     print(response.text, end="")
    #     data_string = data_string + response.text
    #
    #
    # return data_string


def generate_visualisation(document, dataset_id):
    init_vertexai()
    global data_string
    # vertexai.init(project="winged-keyword-441104-q1", location="us-central1")

    responses_viz = model.generate_content(
        ["""
I have a collection of datasets that will be provided as strings in various formats, including CSV, GeoJSON, KML, and KMZ. I need to create appropriate visualizations using Streamlit that are suitable for the data type and maintain a consistent color scheme and design. Here are the specific requirements:
Note, ignore any n/a values or missing values in your analysis. Also note that some datasets might contain headers like 20112 where the year is 2011 but 2 is a superscript. Ignore the last values. Only mention this as a footnote
Geographic Data Visualizations
Point and Polygon Map: Uses points to represent data locations on a map, often with varying sizes or colors.
Heat Map: Shows the density of data points in a geographic area using color gradients.
Bubble Map: Similar to point maps but uses circles of varying sizes to represent data values.
Flow Map: Visualizes movement or flow between locations, often using arrows or lines.
Numerical or Tabular Data Visualizations
Bar Chart: Compares quantities across different categories using rectangular bars.
Line Chart: Shows trends over time or continuous data using lines connecting data points.
Scatter Plot: Displays relationships between two numerical variables using dots.
Histogram: Represents the distribution of numerical data by showing the frequency of data intervals.
Pie Chart: Shows proportions of a whole using slices of a circle.
Box Plot: Summarizes data distributions through their quartiles and highlights outliers.
Heatmap: Represents data in a matrix form using colors to indicate values.
Area Chart: Similar to a line chart but with the area below the line filled in to emphasize volume.
Bubble Chart: Extends a scatter plot by adding a third variable represented by the size of the bubbles.
Violin Plot: Combines a box plot with a kernel density plot to show data distribution.
You are a data analyst. Based on the underlying dataset that you are given, determine which visualization is the appropriate one to render. Then provide back the following requirements for each visualization function
Generate a URL for a Streamlit app that visualizes a dataset. The dataset can be either geospatial or tabular. Based on the dataset type and its columns, choose an appropriate visualization type and map the columns to the required parameters.
Instructions:
Dataset Type:
Determine if the dataset is geospatial or tabular.
Geospatial datasets contain geometry data such as points or polygons.
Tabular datasets contain numerical or categorical data.
Visualization Selection:
For geospatial datasets:
Use point_and_polygon_map if the dataset contains both points and polygons.
Use heat_map for point data to show density.
Use bubble_map to visualize point data with varying sizes.
For tabular datasets:
Use bar_chart for categorical comparisons.
Use line_chart for time series data.
Use scatter_plot for relationships between two numerical variables.
Use histogram for distribution of a single numerical variable.
Use pie_chart for proportional data.
Use box_plot for statistical summaries.
Use area_chart for cumulative data over time.
Use bubble_chart for three-dimensional data comparisons.
Use violin_plot for distribution data.
Parameter Mapping:
Identify the dataset columns and map them to the visualization parameters:
For bar_chart, line_chart, scatter_plot, etc., use x_col, y_col, and optionally category_col.
For bubble_chart, include size_col.
For geospatial visualizations, ensure the dataset has a geometry column.
URL Generation:
Construct the URL with the format:
https://streamlit-app-880265586889.us-central1.run.app/?datasetid=<dataset_id>&viz_type=<viz_type>&x_col=<x_col>&y_col=<y_col>&category_col=<category_col>&size_col=<size_col>
Replace placeholders with actual column headers based on the dataset provided.

Example Prompt
Input: A dataset with columns: Date, Temperature, Humidity, Location.
Output:
Dataset Type: Tabular
Visualization Type: Line Chart (for time series)
Parameter Mapping:
x_col: Date
y_col: Temperature
category_col: Location
Generated URL:
https://streamlit-app-880265586889.us-central1.run.app/?datasetid=123&viz_type=line_chart&x_col=Date&y_col=Temperature&category_col=Location

Return ONLY the URL and nothing else. Do not add any commentary after. Only ever give back the formatted URL. This format MUST be enforced as the URL will be used to parse data to open the appropriate iframe.
Keep the base url the same
""", document,dataset_id],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )
    return responses_viz
