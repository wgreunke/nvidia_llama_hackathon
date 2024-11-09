from newsapi import NewsApiClient
from datetime import datetime

# Initialize the client with your API key

# Fetch articles related to Hurricane Helene
query = 'Hurricane Helene'
#articles = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=5)

query = 'Hurricane Helene'
#source = 'associated-press'
from_date = '2024-09-30'
to_date = '2024-09-30'

# Fetch articles from Associated Press on October 2nd related to Hurricane Helene
api_results = newsapi.get_everything(q=query,from_param=from_date,to=to_date,language='en',sort_by='relevancy')

# Display the articles
if api_results['status'] == 'ok':
    for i, article in enumerate(api_results['articles']):
        print(f"{i+1}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Published At: {article['publishedAt']}")
        print(f"   URL: {article['url']}\n")
else:
    print("Error fetching articles.")

article_list=api_results['articles']



#Loop through the differnet dates and save to csv

with open(articles_csv, 'w') as csvfile:
    #Create a csv writer object
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Title', 'URL', 'Published At'])

    for i in range(10, 23):
      print(i)
      from_date = '2024-10-'+str(i)
      to_date = '2024-10-'+str(i)
      print(from_date)
      print(to_date)
      api_results = newsapi.get_everything(q=query,from_param=from_date,to=to_date,language='en',sort_by='relevancy')
      article_list=api_results['articles']
      print("Number of articles returned")
      print(len(article_list))

      for article in article_list:
        csvwriter.writerow([article['title'], article['url'], article['publishedAt']])
