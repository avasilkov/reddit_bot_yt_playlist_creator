from login_bot import login
from core import update_subreddit_archive

credentials_filename = 'bot_credentials.ini'

LOGIN = True
if LOGIN:
    print('Logging in..')
    r = login(credentials_filename)
    print('Log in as', r.get_me().name, 'successfull!\n')
else:
    #if you don't need to post or comment on reddit, just fetch subreddit submissions
    print('Accessing Reddit without login')
    import praw
    r = praw.Reddit("User-Agent: your_OS:bot_name:v0.1 (by/u/your_name)")


subreddit_names = ['ALifeSimsOnYT']

for subreddit_name in subreddit_names:
    yt_posts = update_subreddit_archive(r, subreddit_name)

