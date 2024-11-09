# ----------------------------------------------Connecting to NVIDIA -----------------------------------------------

from openai import OpenAI
import json
from llama_index.readers.web import SimpleWebPageReader  # Correct import from llama_index.readers.web


prompt = """
Read this article about hurricane Helene. Output only a JSON array that summarizes each news item, using the structure provided below.
For each news item, include the location, event, date-of-event, picture caption, picture link, and latitude/longitude in decimal format.
No additional text should be included in the output; return only a JSON array.
For the date, use the format 2024-09-23.  If the date is not known, use the date from the publication of the article.
For the summary write two to four sentences that sumarize the specific event in the article.
For the source, use the name of the website that published the article.

Error handling.  If you receive a website with information that is not related to hurricane, return an empty JSON array which can still be parsed as a valid JSON array.

Example format:
[
  {
    "city": "Fort Lauderdale",
    "state": "Florida",
    "event": "Flooding",
    "summary":"There was extensive flooding along the river bank.  Multiple cars were washed away.  2 houses were damaged.",
    "lat": "26.1201",
    "lon": "-80.1372",
    "article_url":"https://apnews.com/article/hurricane-helene-north-carolina-national-guard-7dd82ee953d8da9098996231f619cbce",
    "source":"AP News",
    "date-of-event": "2024-09-23",
    "event-picture-caption": "Flooding in Fort Lauderdale",
    "event-picture-link": "https://www.apnews.com/images/124.jpg"
  }
]

Format the response as valid JSON. Do not include any text before or after the JSON array.
"""

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="" #Use appropriate API key for specific model on NIM
)


def get_events_from_article(article_url):
    # Load document data (assumes SimpleWebPageReader is working as expected)
  documents = SimpleWebPageReader(html_to_text=True).load_data([article_url])

  full_prompt = prompt + documents[0].text

  completion = client.chat.completions.create(
    #model="meta/llama-3.1-405b-instruct",  This model takess too long, try another
    #model="meta/llama-3.2-3b-instruct",  #This not putting cities and states in the correct location in the output.
    model="abacusai/dracarys-llama-3.1-70b-instruct",
    messages=[{"role": "user", "content": full_prompt}],
    temperature=0.2,
    top_p=0.7,
    max_tokens=2024,
    stream=True
    )

# Capture response content
  output_json_string = ""
  for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        output_json_string += chunk.choices[0].delta.content

  # Clean the output string to ensure it only contains the JSON
  output_json_string = output_json_string.strip()
  if output_json_string.startswith("```json"):
      output_json_string = output_json_string[7:]
  if output_json_string.endswith("```"):
      output_json_string = output_json_string[:-3]
  output_json_string = output_json_string.strip()

# Convert JSON string to a Python object with error handling
  events_json=None #Clear data
  try:
    events_json = json.loads(output_json_string)
    if isinstance(events_json, list):
        print("Successfully parsed JSON array:")
        print(json.dumps(events_json, indent=2))  # Pretty print the JSON
    else:
        print("Error: Output is not a JSON array")
  except json.JSONDecodeError as e:
    print(f"Failed to parse JSON. Error: {str(e)}")
    print("Raw output:", output_json_string)
  return events_json


# Load document data (assumes SimpleWebPageReader is working as expected)
documents = SimpleWebPageReader(html_to_text=True).load_data(["https://apnews.com/article/hurricane-helene-north-carolina-national-guard-7dd82ee953d8da9098996231f619cbce"])

news_url="https://apnews.com/article/hurricane-helene-north-carolina-national-guard-7dd82ee953d8da9098996231f619cbce"

#test the function
list_of_events=get_events_from_article(news_url)
print(list_of_events)

# ---------------------------- CSV to Store EVents ------------------------------------------

#Use a simple csv file for the data storage
import datetime
import os


#This function Outputs the date in the format year-month-day 2024-08-03. This gets rid of commas
def convert_date(date_string):
    # Check if the date string is already in the desired format
    if '-' in date_string and len(date_string) == 10:  # Check if date is already in YYYY-MM-DD format
        return date_string  # Return as is if already in correct format
    # Otherwise, convert the date string to a datetime object
    date_obj = datetime.datetime.strptime(date_string, "%B %d, %Y")
    # Format the datetime object as a string
    formatted_date = date_obj.strftime("%Y-%m-%d")
    return formatted_date


#This function takes in a list of events and appends the events to the csv file
csv_file_name="events.csv"
path="/content"
def append_events_to_csv(events, csv_file_name, path):

  #Check if the csv file exists, if not, create a new file.
  if not os.path.exists(os.path.join(path,csv_file_name)):
    with open(os.path.join(path,csv_file_name), "w") as events_file:
      #Create the header
      events_file.write("city,state,event,summary,article_url,source,date-of-event,event-picture-caption,event-picture-link,lat,lon\n")

  #Once the file is open, loop throught the events

  with open(os.path.join(path, csv_file_name), "a") as events_file:
    for event in events:
        events_file.write(
            f"{event['city'].replace(',', '')},"
            f"{event['state'].replace(',', '')},"
            f"{event['event'].replace(',', '')},"
            f"{event['summary'].replace(',', '')},"
            #f"{convert_date(event['date-of-event']).replace(',', '')},"
            f"{event['article_url'].replace(',', '')},"
            f"{event['source'].replace(',', '')},"
            f"{event['date-of-event'].replace(',', '')},"
            f"{event['event-picture-caption'].replace(',', '')},"
            f"{event['event-picture-link'].replace(',', '')},"
            f"{event['lat'].replace(',', '')},"
            f"{event['lon'].replace(',', '')}\n"
        )


# ----------------Test the function --------------------------------
#response_dict=json.loads(response.response)
#print(response_dict)

append_events_to_csv(list_of_events, csv_file_name, path)
#Now open the csv file


#Open the CSV file that has a list of news articles related to helene

file_path="/content/helene_events.csv"

import pandas as pd

df = pd.read_csv(file_path)


for index, row in df.iloc[10:20].iterrows(): # Index 6 to 8 (rows 7 through 9)
  print("Now printing row")
  print(index)
  url=row['Link']
  print(url)
  list_of_events=get_events_from_article(url)
  if list_of_events is not None:
    append_events_to_csv(list_of_events, csv_file_name, path)
    print(list_of_events)
