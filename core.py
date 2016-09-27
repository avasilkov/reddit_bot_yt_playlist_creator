import time
import re
from datetime import datetime
import pytz
import csv
import math

archives_folder = 'archives/'
day_in_seconds = 24*60*60
search_granularity_interval = day_in_seconds
search_query = 'timestamp:{0}..{1}'
timestamp_date_format = '%d/%m/%Y %H:%M:%S'

def get_posts_between(r, subreddit_name, start, end):
    print(start, end)
    search_results = r.search(search_query.format(start, end), subreddit=subreddit_name, sort='new', syntax='cloudsearch')
    return search_results

#http://stackoverflow.com/questions/19377262/regex-for-youtube-url
yt_link_pattern = re.compile("((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)")
def get_yt_links(post):
    if yt_link_pattern.match(post.url):
        return [post.url]
    return list(set([''.join(m) for m in re.findall(yt_link_pattern, post.selftext_html)]))

def get_now_plus_day():
    return int(time.time()) + day_in_seconds

def get_date_str(timestamp, is_utc_needed):
    if is_utc_needed:
        return datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).strftime(timestamp_date_format) + ' UTC'
    else:
        return datetime.utcfromtimestamp(timestamp).strftime(timestamp_date_format) + ' L_TZ'

def print_post(post):
    print('Title:', post[0])
    print('Name:', post[1])
    print('Score:', post[2])
    print('Ups:', post[3])
    print('Downs:', post[4])
    print('Author username:', post[5])
    print('Date UTC:', get_date_str(post[6], True))
    print('Text content:', post[7])
    for i, link in enumerate(post[8]):
        print('Link', str(i + 1) + ':', link)
    print('Permaink:', post[-1])

def clear_str(s):
    r = ''
    for ss in s:
        if ss.isalnum() or ss in '[]_,.;+=/*-+)(*&^%$#@!~`{}""':
            r += ss
        else:
            r += ' '
    return r

def get_archive_name(subreddit_name):
    return archives_folder + 'yt_posts_from_' + subreddit_name + '.csv'

def save_posts_to_csv(yt_posts, subreddit_name, start_timestamp):
    latest_timestamp = 0
    with open(get_archive_name(subreddit_name), 'w', newline='') as csvfile:
        rowwriter = csv.writer(csvfile, delimiter='\t', quotechar='\t', quoting=csv.QUOTE_NONE)
        rowwriter.writerow(['Title', 'Name', 'Score', 'Ups', 'Downs', 'Username', 'Date', 'Plain text', 'Links', 'Permalink'])
        for post in yt_posts:
            row = list(post)
            row[8] = ','.join(post[8])
            row[0] = clear_str(post[0])
            row[7] = clear_str(post[7])
            if row[6] > latest_timestamp:
                latest_timestamp = row[6]
            rowwriter.writerow(row)
        csvfile.write(str(start_timestamp) + '_' + str(latest_timestamp) + '\r\n')
        csvfile.write(str(int(time.time())))

def load_posts_from_csv(subreddit_name):
    start_end_timestamps = [0, 0]
    last_update_timestamp = 0
    posts = []
    filename = get_archive_name(subreddit_name)
    try:
        with open(filename, 'r', newline='') as csvfile:
            rowreader = csv.reader(csvfile, delimiter='\t', quotechar='\t', quoting=csv.QUOTE_NONE)
            rowreader.__next__()#skip column names
            for row in rowreader:
                if len(row) > 1:
                    post = list(row)
                    for ii in [2, 3, 4, 6]:
                        post[ii] = int(row[ii])
                    post[8] = post[8].split(',')
                    posts.append(post)
                else:
                    start_end_timestamps = [int(s) for s in row[0].split('_')]
                    break
            last_update_timestamp = int(rowreader.__next__()[0])
    except (OSError, IOError) as e:
        print('Error occured while trying accessing', filename)
        print('Creating new file', filename)
        print()
        with open(filename, 'w', newline='') as csvfile:
            csvfile.write('0_0\n')
            csvfile.write(str(int(time.time())))

    return posts, start_end_timestamps, last_update_timestamp

def get_yt_posts_and_permalinks_set_between(r, subreddit_name, already_archived_permalinks_set, start_timestamp, end_timestamp):
    posts = list(get_posts_between(r, subreddit_name, start_timestamp, end_timestamp))

    new_yt_posts = []
    new_permalinks_set = set()
    for post in posts:
        permalink = post.permalink.replace('?ref=search_posts','')
        if permalink not in already_archived_permalinks_set and permalink not in new_permalinks_set:
            yt_links = get_yt_links(post)
            if len(yt_links) > 0:
                new_yt_posts.append((post.title, post.name, post.ups - post.downs, post.ups, post.downs, post.author.name, int(post.created_utc), post.selftext, yt_links, permalink))
                new_permalinks_set.add(permalink)

    return new_yt_posts, new_permalinks_set

def update_subreddit_archive(r, subreddit_name):

    yt_posts, start_end_timestamps, last_update_timestamp = load_posts_from_csv(subreddit_name)

    permalinks_set = set([post[-1] for post in yt_posts])

    print('Database has {0} posts total. Range from {1} to {2}'.format(len(yt_posts), get_date_str(start_end_timestamps[0], True), get_date_str(start_end_timestamps[1], True)))
    print('Last update was', get_date_str(last_update_timestamp, False))

    if start_end_timestamps[0] == start_end_timestamps[1] == 0:
        start_timestamp = input('\nPlease enter date from which to start gathering posts. Format ' + timestamp_date_format +
                '\nExample: ' + get_date_str(time.time(), False) + '\n')

        start_end_timestamps[0] = datetime.strptime(start_timestamp, timestamp_date_format).replace(tzinfo=pytz.utc).timestamp()
    else:
        #start_end_timestamps[0] = max(start_end_timestamps[1] - search_granularity_interval, start_end_timestamps[0])
        start_end_timestamps[0] = max(last_update_timestamp - search_granularity_interval, start_end_timestamps[0])

    start_end_timestamps[1] = get_now_plus_day()
    start_end_timestamps[0] = int(start_end_timestamps[0])

    #start_end_timestamps[1] = int(math.ceil((start_end_timestamps[1] - start_end_timestamps[0])/search_granularity_interval)*search_granularity_interval) + start_end_timestamps[0]
    print('Current search granularity interval', search_granularity_interval)
    print(int(math.ceil((start_end_timestamps[1] - start_end_timestamps[0])/search_granularity_interval)), 'intervals to search')
    for current_search_timestamp_step in range(start_end_timestamps[0], start_end_timestamps[1], search_granularity_interval):
        start = current_search_timestamp_step
        end = current_search_timestamp_step + search_granularity_interval
        print('Getting posts between', get_date_str(start, True), 'and', get_date_str(end, True))
        new_yt_posts, new_permalinks_set = get_yt_posts_and_permalinks_set_between(r, subreddit_name, permalinks_set, start, end)
        print('Got', len(new_yt_posts), 'new posts containing youtube links')
        yt_posts.extend(new_yt_posts)
        permalinks_set.update(new_permalinks_set)


    save_posts_to_csv(yt_posts, subreddit_name, start_end_timestamps[0])

    return yt_posts


