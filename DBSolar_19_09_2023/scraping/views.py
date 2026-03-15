#from django.shortcuts import render
#import requests
#from bs4 import BeautifulSoup

#def scrape(request):
#    url = 'https://www.google.com'
#    response = requests.get(url)
#    soup = BeautifulSoup(response.text, 'html.parser')
#    title = soup.title.string
#    context = {'title': title}
#    return render(request, 'scraping/scrape.html', context)

#*/

import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse


def get_website_title(request):
    # Send a GET request to the website
    response = requests.get('https://www.isolarcloud.com/')

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the title of the website
    title = soup.title.string

    # Return the title as the HTTP response
    return HttpResponse(title)
