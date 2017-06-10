#author = Cassandra Pizarro

#get_parser idea from howdoi
#sleep timer is from Dave Rove on stackoverflow

import time
import requests
import ntfy
import argparse

def main():
    starttime = time.time()
    while True:
        parser = get_parser()
        parser_arguments = vars(parser.parse_args())
        keywords, points, timestamp = get_keyData_fromParser(parser_arguments)
        url_toParse = createURLfrom_keyData(keywords, points, timestamp)
        JSONdata = grab_JSON_ofURL(url_toParse)
        list_of_urlTitles, list_of_urlPoints = get_URLtitle_andPoints(JSONdata)
        send_notifications(list_of_urlTitles, list_of_urlPoints)
        sleep_function(starttime)

def check_userInput_forPoints(parser_arguments):
    if (len(parser_arguments['query']) > 1):
        points = parser_arguments['query'].pop()
        if points.isdigit():
            return points
        else:
            print("You didn't enter a number for points!, Will default to 0 points")
            return "0"
    else:
        print("You didn't enter # of points for hits!, Will default to 0 points")
        return "0"


def createURLfrom_keyData(keywords_fromUser, points_fromUser, weekAgo_fromTimestamp):
    domain = 'http://hn.algolia.com/api/v1/'
    query = 'search_by_date?query=' + keywords_fromUser  #get keywords put commas in between
    tags = '&tags=story'
    stories = '&numericFilters=created_at_i>' + str(weekAgo_fromTimestamp)
    points_of_story = ',points>' + points_fromUser
    url_toParse = domain + query + tags + stories + points_of_story
    return url_toParse


def get_keyData_fromParser(parser_arguments):
    points = check_userInput_forPoints(parser_arguments)
    keywords = get_userKeywords(parser_arguments)
    timestamp = get_timestamp()
    return keywords, points, timestamp


def get_parser():
    parser = argparse.ArgumentParser(description='***Hackernews Parser***')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='*',
                        help='FORMAT: keywords with number of points ex. java 100, keywords you are searching for = java,'
                             ' 100 = least # of points you want in a hit')
    return parser


def get_points(JSONdata):
    counter = 0
    url_points = []
    for data in JSONdata['hits']:
        for item, value in JSONdata['hits'][counter].items():
            if item == "points":
                points = "Points: " + str(value)
                url_points.append(points)
        counter += 1
    return url_points


def get_timestamp():
    current_timestamp = time.time()
    weekAgo_fromTimestamp = current_timestamp - 604800
    return weekAgo_fromTimestamp


def get_titles(JSONdata):  #should I make a separate function for points?
    counter = 0
    url_titles = []
    for data in JSONdata['hits']:
        for item, value in JSONdata['hits'][counter].items():
            if item == "title":
                title = "Title: " + str(value)
                url_titles.append(title)
        counter += 1
    return url_titles


def get_URLtitle_andPoints(JSONdata):
    list_of_urlTitles = get_titles(JSONdata)
    list_of_urlPoints = get_points(JSONdata)
    return list_of_urlTitles, list_of_urlPoints


def get_userKeywords(parser_arguments):
    keywords = ""
    for keyword in parser_arguments['query']:
        keywords += keyword + " "
    keywords = keywords.replace(" ", ",")
    keywords = keywords[:-1]
    return keywords


def grab_JSON_ofURL(url_toParse): #grab_JSON_ofURL
    hacker_html_doc = requests.get(url_toParse)
    JSONdata = hacker_html_doc.json()
    return JSONdata


def send_notifications(url_titles, url_points):
    if not url_titles:
        ntfy.notify("No hits were found!", "Hacker News Parser")
        return

    for i in range(len(url_titles)):
        ntfy.notify(url_points[i], url_titles[i])
    return


def sleep_function(starttime):
    sleepTime = 1800.0 - ((time.time() - starttime) % 1800.0)  #1800 = 30 minutes
    time.sleep(sleepTime)
    return sleepTime

if __name__ == '__main__':
    main()
