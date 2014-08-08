#!/usr/bin/env python
import httplib
import StringIO
import hashlib
import uuid
import random
import string
import sys
import os
import subprocess
import gzip
import threading
import logging
from pprint import pformat

if sys.version_info[1] >= 6:
    import json
else:
    import simplejson as json

_useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"
_token = None

URL = "grooveshark.com"
htmlclient = ('htmlshark', '20130520', 'nuggetsOfBaller',
              {"User-Agent": _useragent,
               "Content-Type": "application/json",
               "Accept-Encoding": "gzip"})
jsqueue = ['jsqueue', '20130520', 'chickenFingers']
jsqueue.append({"User-Agent": _useragent,
                "Referer": 'http://%s/JSQueue.swf?%s' % (URL, jsqueue[1]),
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json"})

#Setting the static header (country, session and uuid)
h = {}
h["country"] = {}
h["country"]["CC1"] = 72057594037927940
h["country"]["CC2"] = 0
h["country"]["CC3"] = 0
h["country"]["CC4"] = 0
h["country"]["ID"] = 57
h["country"]["IPR"] = 0
h["privacy"] = 0
h["session"] = (''.join(
    random.choice(string.digits + string.letters[:6])
    for x in range(32)
)).lower()
h["uuid"] = str.upper(str(uuid.uuid4()))


#Generate a token from the method and the secret string
#(which changes once in a while)
def prepToken(method, secret):
    rnd = (''.join(random.choice(string.hexdigits) for x in range(6))).lower()
    return rnd + hashlib.sha1('%s:%s:%s:%s' % (method, _token, secret, rnd)).hexdigest()

#Fetch a queueID (right now we randomly generate it)
def getQueueID():
    return random.randint(10000000000000000000000, 99999999999999999999999)

#Get the static token issued by sharkAttack!
def getToken():
    global h, _token
    p = {}
    p["parameters"] = {}
    p["parameters"]["secretKey"] = hashlib.md5(h["session"]).hexdigest()
    p["method"] = "getCommunicationToken"
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    conn = httplib.HTTPSConnection(URL)
    conn.request("POST", "/more.php", json.JSONEncoder().encode(p), htmlclient[3])
    _token = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

#Process a search and return the result as a list.
def getResultsFromSearch(query, what="Songs"):
    p = {}
    p["parameters"] = {}
    p["parameters"]["type"] = what
    p["parameters"]["query"] = query
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("getResultsFromSearch", htmlclient[2])
    p["method"] = "getResultsFromSearch"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    j = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())
    try:
        return j["result"]["result"]["Songs"]
    except:
        return j["result"]["result"]

def getResultsFromPlaylist(query):
    p = {}
    p["parameters"] = {}
    p["parameters"]["playlistID"] = int(query)
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("playlistGetSongs", htmlclient[2])
    p["method"] = "playlistGetSongs"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    resp = conn.getresponse()
    j = json.JSONDecoder().decode(
            gzip.GzipFile(fileobj=(StringIO.StringIO(resp.read()))).read())
    return j["result"]["Songs"]

def getResultsFromAlbum(query):
    p = {}
    p["parameters"] = {}
    p["parameters"]["albumID"] = int(query)
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("albumGetAllSongs", htmlclient[2])
    p["method"] = "albumGetAllSongs"
    post_data = json.JSONEncoder().encode(p)
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], post_data, htmlclient[3])
    resp = conn.getresponse()
    j = json.JSONDecoder().decode(
            gzip.GzipFile(fileobj=(StringIO.StringIO(resp.read()))).read())
    return j["result"]


def getArtistId(profileID):
    p = {}
    p["parameters"] = {}
    p["parameters"]["profileID"] = int(profileID)
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("getProfileInfoByID", htmlclient[2])
    p["method"] = "getProfileInfoByID"

    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    resp = conn.getresponse()
    j = json.JSONDecoder().decode(
            gzip.GzipFile(fileobj=(StringIO.StringIO(resp.read()))).read())
    return j["result"]["artist"]["ArtistID"]

def getArtistSongs(artistID):
    p = {}
    p["parameters"] = {}
    p["parameters"]["artistID"] = int(artistID)
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("artistGetArtistSongs", htmlclient[2])
    p["method"] = "artistGetArtistSongs"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    resp = conn.getresponse()
    j = json.JSONDecoder().decode(
            gzip.GzipFile(fileobj=(StringIO.StringIO(resp.read()))).read())
    return j["result"]

def getItemFromPage(name):
    p = {}
    p["parameters"] = {}
    p["parameters"]["name"] = name
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("getItemByPageName", htmlclient[2])
    p["method"] = "getItemByPageName"

    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    resp = conn.getresponse()
    j = json.JSONDecoder().decode(
            gzip.GzipFile(fileobj=(StringIO.StringIO(resp.read()))).read())
    return j["result"]


#Get all songs by a certain artist
def artistGetSongsEx(id, isVerified):
    p = {}
    p["parameters"] = {}
    p["parameters"]["artistID"] = id
    p["parameters"]["isVerifiedOrPopular"] = isVerified
    p["header"] = h
    p["header"]["client"] = htmlclient[0]
    p["header"]["clientRevision"] = htmlclient[1]
    p["header"]["token"] = prepToken("artistGetSongsEx", htmlclient[2])
    p["method"] = "artistGetSongsEx"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())

#Get the streamKey used to download the songs off of the servers.
def getStreamKeyFromSongIDs(id):
    p = {}
    p["parameters"] = {}
    p["parameters"]["type"] = 8
    p["parameters"]["mobile"] = False
    p["parameters"]["prefetch"] = False
    p["parameters"]["songIDs"] = [id]
    p["parameters"]["country"] = h["country"]
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("getStreamKeysFromSongIDs", jsqueue[2])
    p["method"] = "getStreamKeysFromSongIDs"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]


#Add a song to the browser queue, used to imitate a browser
def addSongsToQueue(songObj, songQueueID, source='user'):
    queueObj = {}
    queueObj["songID"] = songObj["SongID"]
    queueObj["artistID"] = songObj["ArtistID"]
    queueObj["source"] = source
    queueObj["songQueueSongID"] = 1
    p = {}
    p["parameters"] = {}
    p["parameters"]["songIDsArtistIDs"] = [queueObj]
    p["parameters"]["songQueueID"] = songQueueID
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("addSongsToQueue", jsqueue[2])
    p["method"] = "addSongsToQueue"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]


#Remove a song from the browser queue
#used to imitate a browser, in conjunction with the one above.
def removeSongsFromQueue(songQueueID, userRemoved = True):
    p = {}
    p["parameters"] = {}
    p["parameters"]["songQueueID"] = songQueueID
    p["parameters"]["userRemoved"] = True
    p["parameters"]["songQueueSongIDs"]=[1]
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("removeSongsFromQueue", jsqueue[2])
    p["method"] = "removeSongsFromQueue"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]


#Mark the song as being played more then 30 seconds
#used if the download of a songs takes a long time.
def markStreamKeyOver30Seconds(songID, songQueueID, streamServer, streamKey):
    p = {}
    p["parameters"] = {}
    p["parameters"]["songQueueID"] = songQueueID
    p["parameters"]["streamServerID"] = streamServer
    p["parameters"]["songID"] = songID
    p["parameters"]["streamKey"] = streamKey
    p["parameters"]["songQueueSongID"] = 1
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("markStreamKeyOver30Seconds", jsqueue[2])
    p["method"] = "markStreamKeyOver30Seconds"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
    return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]


#Mark the song as downloaded, hopefully stopping us from getting banned.
def markSongDownloadedEx(streamServer, songID, streamKey):
    p = {}
    p["parameters"] = {}
    p["parameters"]["streamServerID"] = streamServer
    p["parameters"]["songID"] = songID
    p["parameters"]["streamKey"] = streamKey
    p["header"] = h
    p["header"]["client"] = jsqueue[0]
    p["header"]["clientRevision"] = jsqueue[1]
    p["header"]["token"] = prepToken("markSongDownloadedEx", jsqueue[2])
    p["method"] = "markSongDownloadedEx"
    conn = httplib.HTTPConnection(URL)
    conn.request("POST", "/more.php?" + p["method"],
                 json.JSONEncoder().encode(p), jsqueue[3])

    try:
        content = gzip.GzipFile(
            fileobj=StringIO.StringIO(conn.getresponse().read())
        ).read()
        res = json.JSONDecoder().decode(content)
    except Exception as exc:
        logging.warning("Unable to mark song as downloaded [%s]" % str(exc))
        return

    try:
        ret = res['result']['Return']
    except Exception as exc:
        logging.exception("Unexpected format for markDownloaded")
        logging.debug(pformat(ret))
        return

    if ret is not True:
        logging.warning("errors marking as downloaded")


def ui_results(query):
    s = getResultsFromSearch(query)
    res_to_show = 30
    l = [
        ('%d: "%s" by "%s" (%s) {ID=%s}' %
         (i, l["SongName"], l["ArtistName"], l["AlbumName"],
          l['SongID']))
        for i, l in enumerate(s[:res_to_show])
    ]  # output strings for first N entries
    if not l:  # If the result was empty print a message and exit
        print "No results found"
        exit(1)
    else:
        print '\n'.join(l)
    songid = raw_input("Enter the Song IDs you wish to download (separated with commas) or (q) to exit: ")
    if songid == "" or songid == "q":
        exit()
    inputtedIDs = songid.split(',')

    for curID in inputtedIDs:
        yield s[int(curID.strip())]

if __name__ == "__main__":
    if os.getenv('GROOVE_DEBUG') == '1':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    getToken()
    queueID = getQueueID()
    if '#!/playlist/' in sys.argv[1]:
        plid = sys.argv[1].rsplit('/', 1)[1]
        logging.info("Playlist detected: %s" % plid)
        songs = getResultsFromPlaylist(plid)
    elif '#!/profile/' in sys.argv[1]:
        plid = sys.argv[1].rsplit('/', 1)[1]
        logging.info("Artist profile detected: %s" % plid)
        songs = getArtistSongs(getArtistId(plid))
    elif '#!/album/' in sys.argv[1]:
        plid = sys.argv[1].rsplit('/', 1)[1]
        logging.info("Album detected: %s" % plid)
        songs = getResultsFromAlbum(plid)
    elif '#!/' in sys.argv[1]:
        #provamoce
        name = sys.argv[1].rsplit('/', 1)[1]
        item = getItemFromPage(name)
        if not item['type']:
            logging.error("Cannot find '%s'" % name)
            sys.exit(1)
        elif item['type'] == 'artist':
            songs = getArtistSongs(item['artist']['ArtistID'])
        else:
            logging.error("Unsupported item type: %s" % item['type'])
            logging.debug(pformat(item))
            sys.exit(1)
    else:
        songs = ui_results(sys.argv[1])
    for song in songs:
        if 'SongName' in song:
            filename = "%s - %s.mp3" % (song["ArtistName"], song["SongName"])
        else:
            filename = "%s - %s.mp3" % (song["ArtistName"], song["Name"])
        if os.path.exists(filename):
            logging.info("File '%s' already exists; skipping" % filename)
            continue
        addSongsToQueue(song, queueID)
        stream = getStreamKeyFromSongIDs(song["SongID"])
        for k, v in stream.iteritems():
            stream = v  # wtf
        if not stream:
            logging.critical("Cannot retrieve stream url for song")
            sys.exit(1)
        cmd = 'wget --post-data=streamKey=%s -O "%s" "http://%s/stream.php"' % \
              (stream["streamKey"],
               filename,
               stream["ip"])
        p = subprocess.Popen(cmd, shell=True)
        #Starts a timer that reports the song as being played for over 30-35 seconds. May not be needed.
        markTimer = threading.Timer(30 + random.randint(0, 5),
                                    markStreamKeyOver30Seconds,
                                    [song["SongID"],
                                     str(queueID),
                                     stream["ip"],
                                     stream["streamKey"]
                                     ]
                                    )
        markTimer.start()

        try:
            p.wait()  # Wait for wget to finish
        except KeyboardInterrupt:  # If we are interrupted by the user
            try:
                os.remove(filename)
                logging.info("\nDownload cancelled. File deleted.")
            except:
                pass

        markTimer.cancel()
        logging.debug("Marking song as completed")
        #This is the important part
        #hopefully this will stop grooveshark from banning us.
        markSongDownloadedEx(stream["ip"], song["SongID"], stream["streamKey"])
