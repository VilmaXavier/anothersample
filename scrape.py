import requests
from bs4 import BeautifulSoup
import json

# URL to scrape
url = "https://xaviers.ac/"

# Send GET request to fetch the content
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Scraping paragraph texts
    paragraphs = [para.get_text() for para in soup.find_all('p')]
    
    # Scraping links
    links = [link['href'] for link in soup.find_all('a', href=True)]
    
    # Creating a dictionary to store the scraped data
    data = {
        "paragraphs": paragraphs,
        "links": links
    }
    
    # Save the data to a JSON file
    with open("college_data1.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print("Scraped data saved to 'college_data1.json'")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
