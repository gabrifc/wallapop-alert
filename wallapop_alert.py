#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import demiurge, sys, getopt, os, pickle, tempfile

urlWallapop = 'http://es.wallapop.com'
urlWallapopMobile = 'http://p.wallapop.com/i/'
savePath = os.path.join(tempfile.gettempdir()) + '/'

pushToken = '<your token>'
email = '<your email>'
saveData = True
push_bullet = False

# Demiurge for get products in Wallapop
class Products(demiurge.Item):
    title = demiurge.TextField(selector='a.product-info-title')
    price = demiurge.TextField(selector='span.product-info-price')
    url = demiurge.AttributeValueField(selector='div.card-product-product-info a.product-info-title', attr='href')

    class Meta:
        selector = 'div.card-product'

class ProductDetails(demiurge.Item):
    description = demiurge.TextField(selector='p.card-product-detail-description')
    location = demiurge.TextField(selector='div.card-product-detail-location')

    class Meta:
        selector = 'div.card-product-detail'

def sendPushBullet(pushToken, email, title, body, url):
    command = "curl -X POST -H 'Access-Token: {pushToken}' -F 'type=link' -F 'title={title}' -F 'body={body}' -F 'url={url}' -F 'email={email}' 'https://api.pushbullet.com/v2/pushes'".format(pushToken = pushToken, email=email, title=title, body=body, url=url)
    os.system(command)

def wallAlert(urlSearch, SAVE_LOCATION):
    data_temp = []
    # Load after data search
    try:
        dataFile = open(SAVE_LOCATION, 'rb')
        data_save = pickle.load(dataFile)
        dataFile.close()
    except:
        data_save = []

    # Read web
    results = Products.all(urlSearch)

    for item in results:
        data_temp.append({'title': item.title
                          , 'price': item.price
                          , 'relativeUrl': item.url })

    # Check new items
    list_news = []
    for item in data_temp:
        if item not in data_save:
            list_news.append(item)
            # Save into the db
            data_save.append(item)

    # Save data
    dataFile = open(SAVE_LOCATION, 'wb')
    if saveData:
        pickle.dump(data_save, dataFile)
    else:
        pickle.dump(data_temp, dataFile)
    dataFile.close()

    for item in list_news:
        # Get info from new items
        title = item['title'] + " - " + item['price']
        title = title.encode('utf-8')
        url = urlWallapop + item['relativeUrl']
        itemDetails = ProductDetails.one(url)
        body = itemDetails.description + "\n" + itemDetails.location
        body = body.encode('utf-8')
        productID = url.split("-")[-1]
        applink = urlWallapopMobile + productID

        # Send Alert
        print(title, body, url)
        print('-' * 10)
        if push_bullet:
            sendPushBullet(pushToken, email, title, body, applink)

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
        SAVE_LOCATION = savePath + keyword + '.pkl'
        print('*' * 10)
        print ("Searching", keyword)
        print('*' * 10)
        urlSearch = 'http://es.wallapop.com/search?kws=' + keyword + '&maxPrice=&dist=0_&order=creationData-des&lat=41.398077&lng=2.170432'
        wallAlert(urlSearch, SAVE_LOCATION)

if __name__ == "__main__":
    main(sys.argv[1:])
