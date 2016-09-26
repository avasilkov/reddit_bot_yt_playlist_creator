# Reddit bot yt playlists creator W.I.P
Reddit bot, that finds all youtube video links in a subreddit and creates a youtube playlists. Has oauth implemented as well.

Here's example of bot_credentials.ini for oauth if you need to post or reply on reddit:

```
user_agent_info = User-Agent: your_OS:bot_name:v0.1 (by/u/your_name)
client_id = given by reddit
client_secret = given by reddit
redirect_uri = http://127.0.0.1:65010
scopes = read identity
refresh_token = if you don't have it, don't include this line, it will be added on first load
```
