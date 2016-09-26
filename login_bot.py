import praw
import configparser

def get_refresh_token(r, scopes):
    #r - praw instance, scopes - scopes
    url = r.get_authorize_url('uniqueKey', scopes, True)
    import webbrowser
    webbrowser.open(url)
    url = input('Copy and paste whole redirected url here=\n')
    from urllib.parse import urlparse, parse_qs
    o = urlparse(url)
    query = parse_qs(o.query)
    if 'code' in query:
        code = query['code']
    else:
        print('there is an error in your redirect link with code parameter, check if it exists')
        exit()
    access_information = r.get_access_information(code)
    return access_information['refresh_token']

def load_credentials(filename):
    credentials = configparser.ConfigParser()
    with open(filename, 'r') as configfile:
        credentials.read_string('[dummy_section]\n' + configfile.read())
    credentials = dict(credentials['dummy_section'])
    credentials['scopes'] = credentials['scopes'].split(' ')
    return credentials

def login(credentials_filename):
    credentials = load_credentials(credentials_filename)

    r = praw.Reddit(credentials['user_agent_info'])
    r.set_oauth_app_info(client_id=credentials['client_id'],
                         client_secret=credentials['client_secret'],
                         redirect_uri=credentials['redirect_uri'])

    if 'refresh_token' not in credentials:
        #https://www.reddit.com/r/redditdev/comments/3fbqfw/oauth_help_for_simple_python_bots_getting_invalid/
        credentials['refresh_token'] = get_refresh_token(r, credentials['scopes'])
        with open(credentials_filename, 'a') as f:
            f.write('refresh_token = ' + credentials['refresh_token'])

    r.refresh_access_information(credentials['refresh_token'])

    #token updates will happen automatically from this point
    return r

