
#
#
# Idea is to display n Up Next videos from a given YouTube entry.


import argparse
import urlparse
import requests
from bs4 import BeautifulSoup
import json
import random

random.seed( )

ap = argparse.ArgumentParser()
ap.add_argument("-k","--key", help="API key")
ap.add_argument("-i","--videoID", help="starting video Key")
ap.add_argument("-u","--videoURL", help="starting video URL")
ap.add_argument("-t","--titles", action='store_true', help="display each upnext title as well as url/ID")

ap.add_argument("-c","--count", default=12, type=int, help="number of upnext items to search")
ap.add_argument("-s","--show", default=3, type=int, help="number of upnext items to display")
ap.add_argument("-d","--depth", default=5, type=int, help="upnext items to traverse")
ap.add_argument("-r","--random", action='store_true', help="randomly choose upnext item (default is first).  If random, chosen entry is displayed with random value")

args = vars( ap.parse_args() )

video_id = args[ 'videoID' ]
video_url = args['videoURL']
youtube_key = args['key']


#
# url = "http://www.youtube.com/watch?v=%s" % video_id
def youtube_url( url ):
    response = requests.get( url )
    if response.status_code == 200:
        parsed_url =  urlparse.urlparse(url)
        vID = urlparse.parse_qs(parsed_url.query)['v']
        return ( response.content, youtube_thumbnails( vID ) )
    return None


#
#
def youtube_thumbnails( video_id ):

    results = None
    thumbnails = None
    url_list = []
    
    api_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CrecordingDetails&"
    api_url += "id=%s&" % video_id
    api_url += "key=%s" % youtube_key

    response = requests.get(api_url)

    if response.status_code == 200:
        results = json.loads( response.content )

        thumbnails = results['items'][0]['snippet']['thumbnails']
        for thumbnail in thumbnails:
            url_list.append( thumbnails[thumbnail]['url'] )

    return url_list


#
# related-list-item
def youtube_upnextlist( url ):
    soup = BeautifulSoup( video_data, 'html.parser' )

    unl = []
    for item in soup.find_all('li', class_="related-list-item"):
        if item.div is not None:
            unl.append( [ item.div.a['title'], item.div.a['href'] ] )

    return unl
    


#
#
#
if None != video_url:
    source_video = video_url

elif None != video_id:
    source_video = "https://www.youtube.com/watch?v=%s" % video_id

else:
    print "[*] no URL or ID given."
    exit

print "[*] Source Video: %s" % source_video


thumbnails = []
(video_data,thumbnails) = youtube_url( source_video )

if video_data is None:
    print( "[!] %s didn't return any data." % souece_video )

elif thumbnails:
    for thumb in thumbnails:
        print "[*]  thumbnail: %s" % thumb
        
print "========================="

print "Depth: ", args['depth'], "Count: ", args['count']
for depth in range( args['depth'] ):

    if args['random']:
        NextJump = random.randint( 0, args['count'] )
    else:
        NextJump = 0

    upnextlist = youtube_upnextlist( video_data )

    tabs = "   " * depth
    if args['random']:
        print "%s #%d --> %s @ %s." % ( tabs, NextJump, upnextlist[NextJump][0], upnextlist[NextJump][1] )
    for upnext in upnextlist[0:args['show']]:
        if args['titles']:
            print "%s[*] %s @ %s." % ( tabs, upnext[0][:50], upnext[1] )
        else:
            print "%s[*] http://www.youtube.com%s." % ( tabs, upnext[1] )

    

    (video_data, thumbs) = youtube_url( "http://www.youtube.com%s" % upnextlist[NextJump][1] )

    
