from login_bot import login
import time
import re
import pickle
from datetime import datetime

day_in_seconds = 24*60*60

def get_posts_between(r, subreddit_name, start, end):
    interaval_tuple = (start, end)
    search_results = r.search(search_query.format(*interaval_tuple), subreddit=subreddit_name, sort='new', syntax='cloudsearch')
    return search_results

#http://stackoverflow.com/questions/19377262/regex-for-youtube-url
yt_link_pattern = re.compile("((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)")
def get_yt_links(post):
    if yt_link_pattern.match(post.url):
        return [post.url]
    return list(set([''.join(m) for m in re.findall(yt_link_pattern, post.selftext_html)]))


credentials_filename = 'bot_credentials.ini'

r = login(credentials_filename)
print('Login as', r.get_me().name, 'successfull!\n')
#subreddit_name = 'ALifeSimsOnYT'
subreddit_name = 'testingground4bots'
#posts = r.get_submissions(subreddit_name, limit=1000)
#for post in posts:
#    print(post)
search_query = 'timestamp:{0}..{1}'

search_interval = day_in_seconds

#timestamps_saved, yt_posts = pickle.load(open('yt_posts_from_' + subreddit_name + '.p', 'rb'))
timestamps_saved = (0, 100)
def get_now_plus_day():
    return int(time.time()) + day_in_seconds
yt_posts = []
permalinks_set = set([post[2] for post in yt_posts])

start = get_now_plus_day() - search_interval
end = get_now_plus_day()
posts = list(get_posts_between(r, subreddit_name, start, end))

for post in posts:
    permalink = post.permalink.replace('?ref=search_posts','')
    if permalink not in permalinks_set:
        yt_links = get_yt_links(post)
        if len(yt_links) > 0:
            yt_posts.append((post.title, post.name, permalink, post.ups - post.downs, post.ups, post.downs, post.author.name, int(post.created_utc), yt_links))
            permalinks_set.add(permalink)

for post in yt_posts:
    print('Title:', post[0])
    print('Name:', post[1])
    print('Permaink:', post[2])
    print('Score:', post[3])
    print('Ups:', post[4])
    print('Downs:', post[5])
    print('Author username:', post[6])
    print('Date UTC+my TM:', datetime.fromtimestamp(post[7]).strftime('%d/%m/%Y %H:%M:%S'))
    for i, link in enumerate(post[8]):
        print('Link', str(i + 1) + ':', link)
#pickle.dump((timestamps_saved[0], int(time.time()), yt_posts), open('yt_posts_from_' + subreddit_name + '.p', 'wb'))


