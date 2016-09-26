from login_bot import login
import time

credentials_filename = 'bot_credentials.ini'

r = login(credentials_filename)
print('Login as', r.get_me().name, 'successfull!')
subreddit_name = 'ALifeSimsOnYT'
#posts = r.get_submissions(subreddit_name, limit=1000)
#for post in posts:
#    print(post)
search_query = 'timestamp:{0}..{1}'

search_interval = 1*24*60*60#created_at_utc

interaval_tuple = (int(time.time()) - search_interval*2, int(time.time()))
print(interaval_tuple)

search_result = r.search(search_query.format(*interaval_tuple), subreddit=subreddit_name, sort='new', syntax='cloudsearch')

for post in list(search_result)[:1]:
    print(post.url)
