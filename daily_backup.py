import sys, json, re, urllib2, datetime, os
from urlparse import urlparse

import requests
from bs4 import BeautifulSoup

# two helper function to enable us to make a weekly backups of all archives
# created by obama in his jan 5 hlr piece
# http://harvardlawreview.org/2017/01/the-presidents-role-in-advancing-criminal-justice-reform/

reload(sys)
sys.setdefaultencoding('utf-8')

api_key = ''

def get_perma_address():
    # Translate the perma guids to original urls
    obamurl = 'http://harvardlawreview.org/2017/01/the-presidents-role-in-advancing-criminal-justice-reform/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }

    r = requests.get(obamurl, headers=headers)
    markup = r.text

    soup = BeautifulSoup(markup, "html.parser")
    archives = []
    for link in soup.findAll('a', href=True):
        if 'perma.cc' in link.get('href'):
            guid = link.string[-9:]

            if link.string not in archives:
                params = {'api_key': api_key}

                url = 'https://api.perma.cc/v1/public/archives/%s' % guid
                r = requests.get('https://api.perma.cc/v1/public/archives/%s' % guid, params = params)

                if r.status_code == 200:
                    print r.url, r.text[0:20]
                    details = json.loads(r.text)    

                    archive = {'guid': guid,
                               'title': details['title'],
                               'history': [details['creation_timestamp']],
                               'url': details['url'],
                               }
                    archives.append(archive)
                else:
                    print "%s is likely private" % guid

    with open('data.json', 'w') as outfile:
        json.dump(archives, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    print len(archives)


def get_archives():
    # create a new perma archive for each  url in obama's hlr criminal justice piece
    # this'll run weekly

    with open('collections/data.json', 'r') as data_file:
        archive_data = json.load(data_file)


    counter = 0
    for archive in archive_data:
        payload = {'url': archive['url'],
                  'title': archive['title'],
                  'api_key': api_key,
                  'content-type': 'application/json',
                  'folder': 18374,
                  }

        r = requests.post('https://api.perma.cc/v1/archives/', data=payload)
        #print "%s for %s" % (r.status_code, archive['url'])
        new_archive_details = json.loads(r.text)
        archive['history'].append({new_archive_details['guid']: new_archive_details['archive_timestamp']})
        counter += 1
        print "archived %s links" % counter
        

    
    i = datetime.datetime.now()
    date_string = "%s%s%s%s" % (i.year, i.month, i.day, i.hour)
    new_data_file_path = 'collections/%s-data.json' % date_string


    with open(new_data_file_path, 'w') as outfile:
        json.dump(archive_data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    os.rename(new_data_file_path, 'collections/data.json')

        

#get_perma_address()

get_archives()