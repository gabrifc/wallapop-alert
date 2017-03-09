#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, sys, getopt, os, json, pickle

urlWallapop = 'http://es.wallapop.com'
urlWallapopMobile = 'http://p.wallapop.com/i/'
urlAPI = 'http://es.wallapop.com/rest/items?minPrice=&maxPrice=&dist=0_&order=creationDate-des&lat=41.398077&lng=2.170432&kws='
savePath = os.path.dirname(os.path.realpath(__file__)) + '/dbs/'

pushToken = '<your token here>'
channelTag = '<your channel here>'
saveData = True
push_bullet = True


# 0. Reusable functions

# getUrl: downloads the source code of an URL / API call
def getUrl(url):
    with urllib.request.urlopen(url) as url:
        # return url.read()
        source = url.read().decode('utf-8')
    return source

# translateJson: Converts the string to a json dictionary
def translateJson(string):
    return json.loads(string)

# importJSON: Loads a JSON File as a Dict
def importJSON(file):
    with open(file) as dataFile:
        #return json.load(data_file)
        data = json.load(dataFile)
    return data

# dumpJSON: Writes a JSON File
def dumpJSON(data, file):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

# sendPushBullet: Send the notification via pushbullet
def sendPushBullet(pushToken, channelTag, title, body, url):
    command = "curl -X POST -H 'Access-Token: {pushToken}' -F 'type=link' -F 'title={title}' -F 'body={body}' -F 'url={url}' -F 'channel_tag={channel}' 'https://api.pushbullet.com/v2/pushes'".format(pushToken = pushToken, channel=channelTag, title=title, body=body, url=url)
    #print(command)
    os.system(command)

# wallAlert, main function
def wallAlert(urlSearch, jsonDBFile):

    # Read the db
    try:
        jsonDB = importJSON(jsonDBFile)
    except:
        jsonDB = {}

    # List for the new items
    newItemsList = []

    # To prevent unnecesary functions:
    itemsInDb = jsonDB.keys()
    
    # API Call
    results = translateJson(getUrl(urlSearch))

    # Process JSON
    for item in results['items']:
        product = {}
        product['itemId'] = str(item['itemId'])
        # Check if the product is new
        if product['itemId'] not in itemsInDb:
            # Is new, get info
            product['title'] = item['title']
            product['price'] = item['price']
            product['description'] = item['description']
            product['url'] = item['url']
            product['pictureURL'] = item['pictureURL']
            product['location'] = item['itemLocation']['fullAddress']
            # Append to the new items list
            newItemsList.append(product)
            # New item, put it in the db
            jsonDB[product['itemId']] = product

    # Update the db
    if saveData:
        dumpJSON(jsonDB, jsonDBFile)

    for item in newItemsList:
        # Get info from new items
        title = item['title'] + " - " + item['price']
        url = urlWallapop + '/item/' + item['url']
        body = item['description'] + "\n" + item['location']
        applink = urlWallapopMobile + item['itemId']

        # Parse the strings for url calls
        title = title.replace("'", "")
        body = body.replace("'", "")

        print(title, body, url)
        print('-' * 10)
        if push_bullet:
            sendPushBullet(pushToken, channelTag, title, body, applink)

def usage():
    print ("Usage:", __file__," -k <keywords file or list separated by comma>")

def extractArguments(argv):
    # Get variables
    keywordList = []

    try:
        opts, args = getopt.getopt(argv, "k:", ["keywords="])

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-k", "--keyword"):
            # See if is a file
            try:
                with open(arg) as f:
                  keywordList = [item.strip('\n') for item in f.readlines()]
                # It wasn't a file
            except:
                argSplit = arg.split(',')
                for item in argSplit:
                    # Remove leading spaces
                    item = item.strip()
                    keywordList.append(item)

    if len(keywordList) < 1:
        usage()
        sys.exit()

    return keywordList

def main(argv):
    # Process command line arguments
    keywordList = extractArguments(argv)

    # Loop through keywords
    for keyword in keywordList:
        # Fix the keyword
        keyword = keyword.replace(" ", "+")

        # Get the db file
        jsonDBFile = savePath + keyword + '.json'

        # Get the API url
        urlSearch = urlAPI + keyword

        # Start the search
        print ('*' * 10)
        print ("Searching", keyword)
        print (urlSearch)

        wallAlert(urlSearch, jsonDBFile)

if __name__ == "__main__":
    main(sys.argv[1:])
