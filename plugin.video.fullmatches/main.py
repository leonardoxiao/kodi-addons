# -*- coding: utf-8 -*-
# Module: default
# Author: PureSpin
# Created on: 16.02.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import re
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

URL = 'http://www.fullmatchesandshows.com'

THUMBNAIL = 'icon.png'

def get_categories():
    """
    Get the list of match categories.
    Here you can insert some parsing code that retrieves
    the list of match categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.
    :return: list
    """
    req = urllib2.Request(URL, headers=HEADERS) 
    con = urllib2.urlopen( req )
    content = con.read()
    soup = BeautifulSoup(content, "html.parser")

    items = []
    main_menu_1 = soup.find("ul", {"id":"menu-main-menu-1"})
    for li in main_menu_1.find_all("li"):
        item = {}
        if li.text == "HOME":
            item['name'] = 'Latest Hightlights and Full Matches'
            item['url'] = li.find("a")['href']
            items.append(item)
        else:
            sub_menu = li.find("ul", class_="sub-menu")
            if sub_menu == None:
                # We will skip the rest (live football, humor etc) for now
                continue
            else:
                for sub_item in sub_menu.find_all("li"):
                    item = {}
                    item['name'] = sub_item.text
                    item['url'] = sub_item.find("a")['href']
                    items.append(item)

    return items


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
        #width = media['width']
        #height = media['height']

        url = '{0}/{1}'.format(base_url, media_url)
        break

    return url


def ajax_get_video(acp_pid, acp_currpage):
    print("ajax_get_video({0}, {1})".format(acp_pid, acp_currpage))

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
    if script != None and script.has_attr('data-config'):
        url = script['data-config']
        return url

    return None

def ajax_get_next_page(td_block_id, td_atts, td_column_number, td_block_type, td_current_page):
    print("ajax_get_next_page({0}, {1})".format(td_block_id, td_current_page))

    url = 'http://www.fullmatchesandshows.com/wp-admin/admin-ajax.php'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = { 'User-Agent' : user_agent, 'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' }

    params = {'action': 'td_ajax_block', 'td_atts': td_atts, 'td_block_id': td_block_id, 'td_column_number': td_column_number, 'td_current_page': td_current_page, 'block_type': td_block_type, 'td_filter_value=': '', 'td_user_action': ''}
    req = urllib2.Request(url, urllib.urlencode(params), headers)
    con = urllib2.urlopen(req)
    content = con.read()
    return content

def get_match_options(match_url):
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

    #for td_block in soup.find_all("div", class_=re.compile("^td_module_mx\d+")):
    for li in soup.find_all("li", id=re.compile("^item\d+")):
        print("=====li="+li.text)
        #print("=====li.parent="+li.parent.decode_contents(formatter="html"))
        #print("=====li.parent.parent="+li.parent.parent.parent.decode_contents(formatter="html"))

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
            print("=====data-config1={0}".format(url))
    else:
        for script in soup.find_all("script"):
            if script.has_attr('data-config'):
                url = script['data-config']
                print("=====data-config2={0}".format(url))

    acp_post = soup.find("input", id="acp_post")
    acp_shortcode = soup.find("input", id="acp_shortcode")

    paging_menu = soup.find("ul", id="acp_paging_menu")
    if paging_menu != None:
        #for li in paging_menu.find_all("li"):
        for li in soup.find_all("li", id=re.compile("^item\d+")):
            print("=====li="+li.text)
            item = {}
            item['thumb'] = img
            item['name'] = li.find("div", class_="acp_title").text
            item['genre'] = 'soccer'    # TODO
            #item['id'] = li['id']

            li_class = li['class']
            if len(li_class) > 1 and li_class[1] == 'active':
                print("=====(active)url="+url)
                #item['video'] = url
                # Hack: this is the correct JSON url for the active video.
                # But in order to work with all the other inactive videos,
                # we will pass the URL again to get the JSON url the same way as other videos
                item['video'] = match_url
            else:
                href = li.find("a")['href']
                print("=====href="+href)
                item['video'] = href

            items.append(item)

        for item in items:
            print("=====item['video']="+item['video'])
            #if item['video'][0] == '#':
            if True:
                #item['video'] = ajax_get_video(acp_post['value'], item['video'])
                item['video'] = get_match_video_url(item['video'])
                if item['video'] == None:
                    item['name'] += ' - Soon...'


    else:
        item = {}
        item['thumb'] = img
        item['name'] = entry_title.text
        item['video'] = url
        item['genre'] = 'soccer'    # TODO
        items.append(item)

    return items

def get_match_video_url(match_url):
    """
    Get the option of a match.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param match_url: url
    :return: JSON url
    """

    print("=====get_match_video_url({0})".format(match_url))

    req = urllib2.Request(match_url, headers=HEADERS) 
    con = urllib2.urlopen( req )
    soup = BeautifulSoup(con.read(), "html.parser")

    #for td_block in soup.find_all("div", class_=re.compile("^td_module_mx\d+")):
    for li in soup.find_all("li", id=re.compile("^item\d+")):
        print("=====li="+li.text)
        #print("=====li.parent="+li.parent.decode_contents(formatter="html"))
        #print("=====li.parent.parent="+li.parent.parent.parent.decode_contents(formatter="html"))

    # title
    entry_title = soup.find("h1", class_="entry-title")

    # thumbnail
    img = 'icon.png'
    wpb_wrapper = soup.find("div", class_="wpb_wrapper")
    if wpb_wrapper != None:
        img = wpb_wrapper.find("img")['src']

    # video URL
    url = None
    acp_content = soup.find("div", id="acp_content")
    if acp_content != None:
        script = acp_content.find("script")
        if script != None and script.has_attr('data-config'):
            url = script['data-config']
            print("=====data-config1={0}".format(url))

    if url == None:
        for script in soup.find_all("script"):
            if script.has_attr('data-config'):
                url = script['data-config']
                print("=====data-config2={0}".format(url))

    return url

    acp_post = soup.find("input", id="acp_post")
    acp_shortcode = soup.find("input", id="acp_shortcode")

    paging_menu = soup.find("ul", id="acp_paging_menu")
    if paging_menu != None:
        #for li in paging_menu.find_all("li"):
        for li in soup.find_all("li", id=re.compile("^item\d+")):
            print("=====li="+li.text)
            item = {}
            item['thumb'] = img
            item['name'] = li.find("div", class_="acp_title").text
            item['genre'] = 'soccer'    # TODO
            #item['id'] = li['id']

            li_class = li['class']
            if len(li_class) > 1 and li_class[1] == 'active':
                print("=====(active)url="+url)
                #item['video'] = url
                # Hack: this is the correct JSON url for the active video.
                # But in order to work with all the other inactive videos,
                # we will pass the URL again to get the JSON url the same way as other videos
                item['video'] = match_url
            else:
                href = li.find("a")['href']
                print("=====href="+href)
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
        print("=====item['video']="+item['video'])
        if item['video'][0] == '#':
            #item['video'] = ajax_get_video(acp_post['value'], item['video'])
            item['video'] = get_match_video_url(acp_post['value'], item['video'])
            if item['video'] == None:
                item['name'] += ' - Soon...'

    return items



def get_matches_ajax(block_id, atts, column_number, block_type, current_page):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param category: str
    :return: list
    """
    content = ajax_get_next_page(block_id, atts, column_number, block_type, current_page)
    data = json.loads(content)
    items = get_matches(data['td_data'])

    #data['td_hide_prev']
    if data['td_hide_next'] != 'false':
        item = {}
        item['name'] = 'Next Page'
        item['video'] = None
        try:
            currentPage = int(current_page)
            currentPage += 1
        except ValueError:
            currentPage = 1

        item['url'] = '{0}?action=td_ajax_block&block_id={1}&atts={2}&column_number={3}&block_type={4}&current_page={5}'.format(_url, block_id, atts, column_number, block_type, currentPage)
        items.append(item)
    
    return items


def get_matches(content):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param category: str
    :return: list
    """
    items = []

    soup = BeautifulSoup(content, "html.parser")
    for td_block in soup.find_all("div", class_=re.compile("^td_module_mx\d+")):
        #print("td_block={0}".format(td_block))
        if td_block.find("img") is None:
            continue

        item = {}
        #item['thumb'] = td_block.find("img", itemprop="image")['src']
        item['thumb'] = td_block.find("img")['src']
        #item['name'] = td_block.find("h3", itemprop="name").text
        item['name'] = td_block.find("h3").text
        #item['video'] = td_block.find("a", itemprop="url")['href']
        item['video'] = td_block.find("a")['href']
        #item['date'] = td_block.find("time", itemprop="dateCreated").text
        item['genre'] = 'Soccer'
        items.append(item)

    for td_block in soup.find_all("div", class_="td-block-span4"):
        print("td_block={0}".format(td_block))
        item = {}
        #item['thumb'] = td_block.find("img", itemprop="image")['src']
        item['thumb'] = td_block.find("img")['src']
        #item['name'] = td_block.find("h3", itemprop="name").text
        item['name'] = td_block.find("h3").text
        #item['video'] = td_block.find("a", itemprop="url")['href']
        item['video'] = td_block.find("a")['href']
        #item['date'] = td_block.find("time", itemprop="dateCreated").text
        item['genre'] = 'Soccer'
        items.append(item)

    return items



def get_block_info(content):
    """
    Get the list of videofiles/streams.
    Here you can insert some parsing code that retrieves
    the list of videostreams in a given category from some site or server.

    :param url: url
    :return: block_info
    """
    soup = BeautifulSoup(content, "html.parser")

    item = {}

    # <a href="#" class="td-ajax-next-page" id="next-page-td_uid_1_56da1529a27a1" data-td_block_id="td_uid_1_56da1529a27a1"><i class="td-icon-font td-icon-menu-right"></i></a>
    #td_next_prev_wrap = soup.find("div", class_="td-next-prev-wrap")
    #td_next_page = td_next_prev_wrap.find("a", class_="td-ajax-next-page")
    #td_block_id = td_next_page['data-td_block_id']

    td_block_ids = []
    for div in soup.find_all("div", id=re.compile("^td_uid_\d+_\w+")):
        print("div id={0}, class={1}".format(div['id'], div['class']))
        td_block_ids.append(div['id'])

    if len(td_block_ids) <= 0:
        print("ERROR: failed to find td_block_id!")
        return None

    #subcat_link = soup.find("a", class_="td-subcat-link")
    #td_block_id = subcat_link['data-td_block_id']

    print("=====td_block_ids={0}".format(td_block_ids))

    #for wpb_wrapper in soup.find_all("div", class_="wpb_wrapper"):
    for script in soup.find_all("script"):
        #print("=====wpb_wrapper={0}".format(wpb_wrapper.decode_contents(formatter='html')))
        #script = wpb_wrapper.find("script")
        for td_block_id in td_block_ids:
            if script == None or script.text.find(td_block_id) == -1:
                continue

            scriptText = script.text.replace('\n','').replace('\r','')
            print("=====script={0}".format(scriptText[0:50]))

            # var block_td_uid_1_56da27e59fe1f = new tdBlock();
            # block_td_uid_1_56da27e59fe1f.id = "td_uid_1_56da27e59fe1f";
            # block_td_uid_1_56da27e59fe1f.atts = '{"custom_title":"Latest Highlights and Full Matches","limit":"18","td_ajax_filter_type":"td_category_ids_filter","td_filter_default_txt":"All","ajax_pagination":"next_prev","td_ajax_filter_ids":"499,2,79,28,49,94,65,23,55","category_ids":"94, 65, 218, 233","class":"td_block_id_1997256863 td_uid_1_56da27e59fe1f_rand"}';
            # block_td_uid_1_56da27e59fe1f.td_column_number = "3";
            # block_td_uid_1_56da27e59fe1f.block_type = "td_block_3";
            # block_td_uid_1_56da27e59fe1f.post_count = "18";
            # block_td_uid_1_56da27e59fe1f.found_posts = "3294";
            # block_td_uid_1_56da27e59fe1f.header_color = "";
            # block_td_uid_1_56da27e59fe1f.ajax_pagination_infinite_stop = "";
            # block_td_uid_1_56da27e59fe1f.max_num_pages = "183";
            # tdBlocksArray.push(block_td_uid_1_56da27e59fe1f);

            pattern = '.*block_{0}\.atts\s+\=\s+\'(.*)\'\;.*block_{0}\.td_column_number\s+\=\s+\"(\d+)\"\;.*block_{0}\.block_type\s+\=\s+\"(\w+)\"\;'.format(td_block_id)
            matchObj = re.match(pattern, scriptText)
            if matchObj == None:
                print("ERROR: failed to parse for 'atts' attribute!")
                continue

            td_atts = matchObj.group(1)
            td_column_number = matchObj.group(2)
            td_block_type = matchObj.group(3)
            print("td_atts={0}".format(td_atts))
            print("td_column_number={0}".format(td_column_number))
            print("td_block_type={0}".format(td_block_type))

            item['ajax'] = True
            item['block_id'] = td_block_id
            item['atts'] = td_atts
            item['column_number'] = td_column_number
            item['block_type'] = td_block_type
            break

        if item.has_key('block_id'):
            break
    else:
        print("Warning: failed to find <script> tag! Try traditional hyperlink instead...")
        for page_nav in soup.find_all("div", class_=re.compile("^page-nav.*")):
            current_page = page_nav.find("span", class_="current")
            print("current={0}".format(current_page.text))
            for link in page_nav.find_all("a"):
                if link.find("i", class_="td-icon-menu-right"):
                    print("next_page_url={0}".format(link['href']))
                    item['next_page_url'] = link['href']
                    break
            break
        else:
            if soup.find("div", class_="td-category-grid") or soup.find("div", class_="td-main-content-wrap"):
                print("This page doesn't have the Prev/Next link!")
            else:
                print("ERROR: failed to parse this page!")
                return None

    return item


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
        category_name = category['name']
        category_url = category['url']
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category_name, thumbnailImage=THUMBNAIL)
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
        list_item.setInfo('video', {'title': category_name, 'genre': category_name})
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = '{0}?action=list&category_name={1}&category_url={2}'.format(_url, category_name, category_url)
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


def list_matches_in_category(category_name, category_url):
    """
    Create the list of matches in the Kodi interface.

    :param category_name: str
    :param category_url: url
    """
    # Get the list of videos in the category.

    print("=====list_matches_in_category({0})".format(category_url))
    req = urllib2.Request(category_url, headers=HEADERS) 
    con = urllib2.urlopen( req )
    content = con.read()

    block_info = get_block_info(content)
    if block_info == None:
        return []

    if block_info.has_key('ajax'):
        print("=====ajax!!!")
        current_page = 1
        return list_matches_ajax(block_info['block_id'], block_info['atts'], block_info['column_number'], block_info['block_type'], current_page)
    else:
        print("=====non-ajax!")
        videos = get_matches(content)

        if block_info.has_key('next_page_url'):
            item = {}
            item['name'] = 'Next Page'
            item['video'] = None

            next_page_url = block_info['next_page_url']
            item['url'] = '{0}?action=list&category_name={1}&category_url={2}'.format(_url, category_name, next_page_url)
            print("url={0}".format(item['url']))
            videos.append(item)

        return list_matches(videos)
 

def list_matches_ajax(block_id, atts, column_number, block_type, current_page):
    """
    Create the list of matches in the Kodi interface.
    """
    print("=====list_matches_ajax({0})".format(block_id))

    # Get the list of videos in the category.
    videos = get_matches_ajax(block_id, atts, column_number, block_type, current_page)
    return list_matches(videos)


def list_matches(videos):
    """
    Create the list of matches in the Kodi interface.
    """
    print("=====list_matches()")

    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])

        if video['video'] == None:
            # Non-video item: next page
            url = video['url']

            list_item.setProperty('IsPlayable', 'false')

            # Add the list item to a virtual Kodi folder.
            is_folder = True

        else:
            # Set additional info for the list item.
            list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})

            # Create a URL for the plugin recursive callback.
            url = u'{0}?action=view&match={1}'.format(_url, video['video'])

            # Set 'IsPlayable' property to 'true'.
            # This is mandatory for playable items!
            list_item.setProperty('IsPlayable', 'true')

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


def play_match(match):
    """
    Create the list of playable videos in the Kodi interface.

    :param match: url
    """
    # Get the list of videos in the category.
    videos = get_match_options(match)

    ret = xbmcgui.Dialog().select("Select match options", [video['name'] for video in videos])
    if ret < 0:
        return
    
    # Create a playable item with a path to play.
    path = videos[ret]['video']
    url = get_video(path)
    print("=====Play video: {0}".format(url))
    play_item = xbmcgui.ListItem(path=url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

    return

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
        if video['video'] == None:
            list_item.setProperty('IsPlayable', 'false')
            url = ''
        else:
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
    print("=====params={0}".format(params))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'list':
            # Display the list of matches in a provided category.
            list_matches_in_category(params['category_name'], params['category_url'])
        elif params['action'] == 'td_ajax_block':
            # Display the list of matches using Ajax request.
            list_matches_ajax(params['block_id'], params['atts'], params['column_number'], params['block_type'], params['current_page'])
        elif params['action'] == 'view':
            # Display the list of options for a provided match.
            play_match(params['match'])
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
