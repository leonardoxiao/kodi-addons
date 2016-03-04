# -*- coding: utf-8 -*-
# Module: default
# Author: PureSpin
# Created on: 16.02.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import time
import json
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin

#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
import urllib
import urllib2

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

HEADERS = {'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3"}

URL = 'http://www.fullmatchesandshows.com/'

CATEGORIES = [
    'Latest Hightlights and Full Matches',
    'Competitions',
    'Live Football',
    'Shows',
    'News',
    'Humor'
]

THUMBNAIL = 'icon.png'

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {'Animals': [{'name': 'Crab',
                       'thumb': 'http://www.vidsplay.com/vids/crab.jpg',
                       'video': 'http://www.vidsplay.com/vids/crab.mp4',
                       'genre': 'Animals'},
                      {'name': 'Alligator',
                       'thumb': 'http://www.vidsplay.com/vids/alligator.jpg',
                       'video': 'http://www.vidsplay.com/vids/alligator.mp4',
                       'genre': 'Animals'},
                      {'name': 'Turtle',
                       'thumb': 'http://www.vidsplay.com/vids/turtle.jpg',
                       'video': 'http://www.vidsplay.com/vids/turtle.mp4',
                       'genre': 'Animals'}
                      ],
            'Cars': [{'name': 'Postal Truck',
                      'thumb': 'http://www.vidsplay.com/vids/us_postal.jpg',
                      'video': 'http://www.vidsplay.com/vids/us_postal.mp4',
                      'genre': 'Cars'},
                     {'name': 'Traffic',
                      'thumb': 'http://www.vidsplay.com/vids/traffic1.jpg',
                      'video': 'http://www.vidsplay.com/vids/traffic1.avi',
                      'genre': 'Cars'},
                     {'name': 'Traffic Arrows',
                      'thumb': 'http://www.vidsplay.com/vids/traffic_arrows.jpg',
                      'video': 'http://www.vidsplay.com/vids/traffic_arrows.mp4',
                      'genre': 'Cars'}
                     ],
            'Food': [{'name': 'Chicken',
                      'thumb': 'http://www.vidsplay.com/vids/chicken.jpg',
                      'video': 'http://www.vidsplay.com/vids/bbqchicken.mp4',
                      'genre': 'Food'},
                     {'name': 'Hamburger',
                      'thumb': 'http://www.vidsplay.com/vids/hamburger.jpg',
                      'video': 'http://www.vidsplay.com/vids/hamburger.mp4',
                      'genre': 'Food'},
                     {'name': 'Pizza',
                      'thumb': 'http://www.vidsplay.com/vids/pizza.jpg',
                      'video': 'http://www.vidsplay.com/vids/pizza.mp4',
                      'genre': 'Food'}
                     ]}


def get_categories():
    """
    Get the list of match categories.
    Here you can insert some parsing code that retrieves
    the list of match categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    :return: list
    """
    #return VIDEOS.keys()
    return CATEGORIES


def get_video(video):
    """
    Get the option of a match.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param video: url for the data in JSON
    :  there are 2 types: JSON or URL that we need to navigate to get the JSON link
    :return: video url
    """
    print("=====video_url={0}".format(video))

    #if video[:2] == '//' and video[-4:] == 'json':
    if video[-4:] != 'json':
        #req = urllib2.Request(video, headers={'User-Agent': "Magic Browser"}) 
        req = urllib2.Request(video, headers=HEADERS) 
        con = urllib2.urlopen( req )
        soup = BeautifulSoup(con.read(), "html.parser")

        url = ''
        for script in soup.find_all("script"):
            if script.has_attr('data-config'):
                url = script['data-config']
                break

        video = url
 

    if video[:2] == '//':
        video = 'http:' + video
    print("=====JSON_URL={0}".format(video))

    # JSON
    req = urllib2.Request(video, headers=HEADERS) 
    con = urllib2.urlopen( req )
    data = json.loads(con.read())

    title = data['settings']['title']
    duration = data['duration']

    content = data['content']
    thumbnail = content['poster']
    src = content['media']['f4m']

    # XML
    print("=====media_f4m={0}".format(src))
    req = urllib2.Request(src, headers=HEADERS) 
    con = urllib2.urlopen( req )
    soup = BeautifulSoup(con.read(), "html.parser")

    base_url = soup.find('baseurl').text
    for media in soup.find_all("media"):
        media_url = media['url']
        tbr = media['bitrate']
        width = media['width']
        height = media['height']

        url = '{0}/{1}'.format(base_url, media_url)
        break

    return url


def ajax(acp_pid, acp_currpage):
    print("ajax({0}, {1})".format(acp_pid, acp_currpage))

    url = 'http://www.fullmatchesandshows.com/wp-admin/admin-ajax.php'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = { 'User-Agent' : user_agent, 'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' }

    params = urllib.urlencode({'acp_currpage': acp_currpage, 'acp_pid': acp_pid, 'acp_shortcode': 'acp_shortcode', 'action': 'pp_with_ajax'})
    req = urllib2.Request(url, params, headers)
    con = urllib2.urlopen(req)
    content = con.read()
    print("content={0}".format(content))
    #soup = BeautifulSoup(con.read(), "html.parser")
    soup = BeautifulSoup(content, "html.parser")
    script = soup.find("script")
    if script.has_attr('data-config'):
        url = script['data-config']
        return url

    return None

def get_match(match_url):
    """
    Get the option of a match.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param match_url: url
    :return: list
    """

    print("=====match_url={0}".format(match_url))

    items = []

    req = urllib2.Request(match_url, headers=HEADERS) 
    con = urllib2.urlopen( req )
    soup = BeautifulSoup(con.read(), "html.parser")

    # title
    entry_title = soup.find("h1", class_="entry-title")

    # thumbnail
    img = 'icon.png'
    wpb_wrapper = soup.find("div", class_="wpb_wrapper")
    if wpb_wrapper != None:
        img = wpb_wrapper.find("img")['src']

    # video URL
    url = ''
    acp_content = soup.find("div", id="acp_content")
    if acp_content != None:
        script = acp_content.find("script")
        if script.has_attr('data-config'):
            url = script['data-config']
    else:
        for script in soup.find_all("script"):
            if script.has_attr('data-config'):
                url = script['data-config']

    acp_post = soup.find("input", id="acp_post")
    acp_shortcode = soup.find("input", id="acp_shortcode")

    paging_menu = soup.find("ul", id="acp_paging_menu")
    if paging_menu != None:
        for li in paging_menu.find_all("li"):
            print("=====li="+li.text)
            item = {}
            item['thumb'] = img
            item['name'] = li.find("div", class_="acp_title").text
            item['genre'] = 'soccer'    # TODO
            #item['id'] = li['id']

            li_class = li['class']
            if len(li_class) > 1 and li_class[1] == 'active':
                print("=====url="+url)
                item['video'] = url
            else:
                href = li.find("a")['href']
                item['video'] = href

            items.append(item)

    else:
        item = {}
        item['thumb'] = img
        item['name'] = entry_title.text
        item['video'] = url
        item['genre'] = 'soccer'    # TODO
        items.append(item)

    for item in items:
        if item['video'][0] == '#':
            item['video'] = ajax(acp_post['value'], item['video'][1:])

    #return VIDEOS[category]
    return items


def get_matches(category):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param category: str
    :return: list
    """
    req = urllib2.Request(URL, headers=HEADERS) 
    con = urllib2.urlopen( req )
    content = con.read()
    soup = BeautifulSoup(content, "html.parser")

    td_main = soup.find("div", class_="td-main-content-wrap td-main-page-wrap")
    #print(td_main)

    items = []
    #for td_block in td_main.find_all("div", class_="td-block-span4"):
    for td_block in soup.find_all("div", class_="td-block-span4"):
        item = {}
        item['thumb'] = td_block.find("img", itemprop="image")['src']
        item['name'] = td_block.find("h3", itemprop="name").text
        item['video'] = td_block.find("a", itemprop="url")['href']
        item['date'] = td_block.find("time", itemprop="dateCreated").text
        item['genre'] = category
        items.append(item)

    #return VIDEOS[category]
    return items


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    categories = get_categories()
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category, thumbnailImage=THUMBNAIL)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': THUMBNAIL,
                          'icon': THUMBNAIL,
                          'fanart': THUMBNAIL})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('video', {'title': category, 'genre': category})
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = '{0}?action=list&category={1}'.format(_url, category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    #xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_matches(category):
    """
    Create the list of matches in the Kodi interface.

    :param category: str
    """
    # Get the list of videos in the category.
    videos = get_matches(category)
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['name'], 'genre': video['genre'], 'aired': video['date']})
        list_item.setLabel2(video['date'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        url = '{0}?action=view&match={1}'.format(_url, video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    #xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def view_match(match):
    """
    Create the list of playable videos in the Kodi interface.

    :param match: url
    """
    # Get the list of videos in the category.
    videos = get_match(match)
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        url = '{0}?action=play&video={1}'.format(_url, video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    #xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: str
    """
    # Get the list of videos in the category.
    url = get_video(path)
    print("play_video:url={0}".format(url))

    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'list':
            # Display the list of matches in a provided category.
            list_matches(params['category'])
        elif params['action'] == 'view':
            # Display the list of options for a provided match.
            view_match(params['match'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
