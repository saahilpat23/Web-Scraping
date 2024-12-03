from tld import get_tld
import requests
import re
import csv
import json
import pandas as pd
from bs4 import BeautifulSoup
try: 
    from googlesearch import search 
except ImportError: 
    print("No module named 'google' found")

# Code to google search
search_list = []
# open the web_urls file to clean the already present data   
f = open("web_urls.txt", "r+")  

# absolute file positioning 
f.seek(0)  

# to erase all data  
f.truncate()

m = True
while m:
    s = input('Type y/n whether you want to enter the organization name: ')
    if s == 'y':
        query = input('Enter the organization: ')
        search_list.append(query)
        file = open("web_urls.txt", "a")
        for o in search(query):  # No need for num, stop, pause arguments
            url_site = o
            file.write(url_site)
            file.write('\n')
    if s == 'n':
        m = False 
        print('Thank you...')
        file.close()

# Function to remove duplicates
def remove_dup_email(x):
    return list(dict.fromkeys(x))

def remove_dup_phone(x):
    return list(dict.fromkeys(x))

def get_email(html):
    try:
        email = re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", html)
        nodup_email = remove_dup_email(email)
        return nodup_email
    except:
        pass

def get_phone(html):
    try:
        phone = re.findall(r"(\d{2} \d{3,4} \d{3,4})", html)
        phone1 = re.findall(r"((?:\d{2,3}|\(\d{2,3}\))?(?:\s|-|\.)?\d{3,4}(?:\s|-|\.)\d{4})", html)
        for p in phone1:
            phone.append(p)
        nodup_phone = remove_dup_phone(phone)
        return nodup_phone
    except:
        pass

urls = ''

# Load website URL links
with open('web_urls.txt', 'r') as f:
    for line in f.read():
        urls += line

# Convert a string to a list of URLs
urls = list(filter(None, urls.split('\n')))

# Looping over the URLs
for idx, url in enumerate(urls):  # Use enumerate to get the index (k)
    if idx >= len(search_list):  # If there are more URLs than search queries
        search_name = 'N/A'  # Set a default value if search_list doesn't have a matching query
    else:
        search_name = search_list[idx]  # Get the organization name from search_list corresponding to the URL

    # HTTP requests to the URLs
    res = requests.get(url)
    print(f'Searched home URL: {res.url}') 

    # Parse the response
    info = BeautifulSoup(res.text, 'lxml')

    # Extract contact data from home URL
    emails_home = get_email(info.get_text())
    phones_home = get_phone(info.get_text())

    emails_f = emails_home
    phones_f = phones_home

    # Create a data structure to store the contacts
    contacts_f = {'Searches': search_name, 'website': res.url, 'Email': '', 'Phone': ''}

    # Extract contact link if available
    try:
        contact = info.find('a', text=re.compile('contact', re.IGNORECASE))['href']
        if 'http' in contact:
            contact_url = contact
        else:
            contact_url = res.url[0:-1] + contact

        # Searching contact URL
        res_contact = requests.get(contact_url)
        contact_info = BeautifulSoup(res_contact.text, 'lxml').get_text()

        print(f'Searched contact URL: {res_contact.url}')

        # Extract contact data
        emails_contact = get_email(contact_info)
        phones_contact = get_phone(contact_info)

        # Combining email contacts and email home into a single list
        emails_f = emails_home
        for ele1 in emails_contact:
            emails_f.append(ele1)

        # Combining phone contacts and phone contacts into a single list
        phones_f = phones_home
        for ele2 in phones_contact:
            phones_f.append(ele2)

    except Exception as e:
        print(f"Error processing contact page: {e}")
        pass

    # Removing duplicates
    emails_f = remove_dup_email(emails_f)
    phones_f = remove_dup_phone(phones_f)

    contacts_f['Email'] = emails_f
    contacts_f['Phone'] = phones_f

    # Converting into a data set
    print('\n', json.dumps(contacts_f, indent=2))

    # Dumping the data into the CSV file
    with open('organization_info.csv', 'a') as f:
        # Create CSV writer object
        writer = csv.DictWriter(f, fieldnames=contacts_f.keys())
        # Write rows to the CSV
        writer.writerow(contacts_f)
