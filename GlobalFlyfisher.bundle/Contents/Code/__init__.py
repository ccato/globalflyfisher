TITLE = 'Global Flyfisher Videos'
PREFIX = '/video/globalflyfisher'

ICON = 'icon.png'
ART = 'art.jpg'
URL_PATTERN = 'http://globalflyfisher.com/video/%s?items_per_page=%s&page=%s'

BASE_URL = 'http://globalflyfisher.com'
API_URL = BASE_URL + '/flyfishingvideos/'

CATEGORY_LIST = [
    {'title': 'Fly-Fishing', 'key': 'fishing', 'items_per_page': '12'},
    {'title': 'Fly-Tying', 'key': 'fly-tying', 'items_per_page': '12'}
]


####################################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'AppleTV/7.2 iOS/8.3 AppleTV/7.2 model/AppleTV3,2 build/12F69 (3; dt:12)'
    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)


####################################################################################################
@handler('/video/globalflyfisher', 'Global Flyfisher Videos')
def MainMenu():
    oc = ObjectContainer()
    for category in CATEGORY_LIST:
        oc.add(DirectoryObject(
            key=Callback(VideoList, title=category['title'], category=category['key'],
                         items_per_page=category['items_per_page']),
            title=category['title']
        ))
    return oc


####################################################################################################
def VideoList(title, category, items_per_page, page=1):
    oc = ObjectContainer(title2="%s: %s" % (title, str(page)))
    items = HTML.ElementFromURL(URL_PATTERN % (category, items_per_page, page))
    Log("items = %s" % items)

    for item in items.xpath('//table[@class="views-view-grid cols-3"]/tbody/tr/td'):
        try:
            vtitle = item.xpath('./div[3]/h2/a/text()')[0]
            thumb = item.xpath('./div[2]/div[1]/a/img/@src')[0]
            desc = item.xpath('./div[4]/span/text()')[0]
            vdurl = item.xpath('./div[2]/div[1]/a/@href')[0]

            # Extract the video url by a bit of magic
            lastpos = thumb.rfind('/')
            part1 = thumb[lastpos + 1:]
            part2 = part1.split('?')
            part2 = part2[0].split('.')
            token = part2[0]
            if "youtube" in thumb:
                videourl = "https://www.youtube.com/watch?v=" + token
            else:
                videourl = "https://vimeo.com/" + token

            oc.add(VideoClipObject(
                url=videourl,
                title=vtitle,
                summary=desc,
                thumb=Resource.ContentsOfURLWithFallback(url=thumb)
            ))
        except Exception:
            Log("Ooops")
            continue

    oc.add(NextPageObject(
        key=Callback(
            VideoList,
            title=title,
            category=category,
            items_per_page=items_per_page,
            page=page + 1
        ),
        title="Next Page..."
    ))

    return oc
