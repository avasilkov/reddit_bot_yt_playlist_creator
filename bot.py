from login_bot import login
import time
import re
from datetime import datetime
import csv

day_in_seconds = 24*60*60
credentials_filename = 'bot_credentials.ini'

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

def get_now_plus_day():
    return int(time.time()) + day_in_seconds

def get_date_str(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')

def print_post(post):
    print('Title:', post[0])
    print('Name:', post[1])
    print('Score:', post[2])
    print('Ups:', post[3])
    print('Downs:', post[4])
    print('Author username:', post[5])
    print('Date UTC+my TM:', get_date_str(post[6]))
    for i, link in enumerate(post[7]):
        print('Link', str(i + 1) + ':', link)
    print('Permaink:', post[-1])

def clear_str(s):
    r = ''
    for ss in s:
        if ss.isalnum():
            r += ss
        else:
            r += ' '
    return r

def save_posts_to_csv(yt_posts, subreddit_name, start_end_timestamps):
    with open('yt_posts_from_' + subreddit_name + '.csv', 'w', newline='') as csvfile:
        rowwriter = csv.writer(csvfile, delimiter='\t', quotechar='\t', quoting=csv.QUOTE_MINIMAL)
        rowwriter.writerow(['Title', 'Name', 'Score', 'Ups', 'Downs', 'Username', 'Date', 'Links', 'Permalink'])
        for post in yt_posts:
            row = list(post)
            row[7] = ','.join(post[7])
            row[0] = clear_str(post[0])
            rowwriter.writerow(row)
        csvfile.write(str(start_end_timestamps[0]) + '_' + str(start_end_timestamps[1]) + '\n')

def load_posts_from_csv(subreddit_name):
    with open('yt_posts_from_' + subreddit_name + '.csv', 'r', newline='') as csvfile:
        rowreader = csv.reader(csvfile, delimiter='\t', quotechar='\t', quoting=csv.QUOTE_MINIMAL)
        posts = []
        start_end_timestamps = [0, 0]
        rowreader.__next__()#skip column names
        for row in rowreader:
            if len(row) > 1:
                post = list(row)
                for ii in [2, 3, 4, 6]:
                    post[ii] = int(row[ii])
                post[7] = post[7].split(',')
                posts.append(post)
            else:
                start_end_timestamps = [int(s) for s in row[0].split('_')]
    return posts, start_end_timestamps


subreddit_name = 'ALifeSimsOnYT'
yt_posts, start_end_timestamps = load_posts_from_csv(subreddit_name)
permalinks_set = set([post[-1] for post in yt_posts])

#print('-'*20)
#for post in yt_posts:
#    print_post(post)
#    print('-'*20)

print('Database has {0} posts total. Range from {1} to {2}'.format(len(yt_posts), get_date_str(start_end_timestamps[0]), get_date_str(start_end_timestamps[1])))

"""if you don't need to post or comment on reddit, just fetch subreddit submissions
comment login and uncomment this.
r = praw.Reddit("User-Agent: your_OS:bot_name:v0.1 (by/u/your_name)")
"""
print('Logging in..')
r = login(credentials_filename)
print('Log in as', r.get_me().name, 'successfull!\n')
#subreddit_name = 'testingground4bots'
#posts = r.get_submissions(subreddit_name, limit=1000)
#for post in posts:
#    print(post)
search_query = 'timestamp:{0}..{1}'

search_interval = day_in_seconds

#timestamps_saved, yt_posts = pickle.load(open('yt_posts_from_' + subreddit_name + '.p', 'rb'))
timestamps_saved = (0, 100)

start = get_now_plus_day() - search_interval*2
end = get_now_plus_day()
start_end_timestamps = (start, end)
end_date = end
posts = list(get_posts_between(r, subreddit_name, start, end))

for post in posts:
    permalink = post.permalink.replace('?ref=search_posts','')
    if permalink not in permalinks_set:
        yt_links = get_yt_links(post)
        if len(yt_links) > 0:
            yt_posts.append((post.title, post.name, post.ups - post.downs, post.ups, post.downs, post.author.name, int(post.created_utc), yt_links, permalink))
            permalinks_set.add(permalink)

save_posts_to_csv(yt_posts, subreddit_name, start_end_timestamps)

