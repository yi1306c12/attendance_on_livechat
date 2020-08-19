import json
import requests
import urllib.parse

class YoutubeChat(object):
    """
    """
    def __init__(self, api_key, youtube_url):
        self.api_key = api_key
        self.youtube_id = self.get_video_id(youtube_url)
        self.chat_id = self.get_chat_id(self.api_key, self.youtube_id)
        self.page_token = None

    @staticmethod
    def get_video_id(youtube_url):
        result = urllib.parse.urlparse(youtube_url)
        query_dict = urllib.parse.parse_qs(result.query)
        assert result.netloc == 'www.youtube.com' and result.path == '/watch' and 'v' in query_dict, 'invalid youtube_url:{}'.format(youtube_url)
        return query_dict['v'][0]

    @staticmethod
    def get_chat_id(api_key, youtube_id):#, *, logger=None):
        url = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'key': api_key,
            'id': youtube_id,
            'part': 'liveStreamingDetails'
        }
        data = requests.get(url, params=params).json()
        return data['items'][0]['liveStreamingDetails']['activeLiveChatId']

    def get_chat(self, *, logger=None):
        url = 'https://www.googleapis.com/youtube/v3/liveChat/messages'
        page_token = None
        while True:
            params = {
                'key': self.api_key,
                'liveChatId': self.chat_id,
                'part': 'id,snippet,authorDetails'
            }
            if page_token is not None:
                params['pageToken'] = page_token
            data = requests.get(url, params=params).json()
            yield data
            page_token = data['nextPageToken']

if __name__ == '__main__':
    import sys
    import time
    youtube_url = sys.argv[1]
    with open('settings.json', 'r') as f:
        API_KEY = json.load(f)['API_KEY']
    youtube_chat = YoutubeChat(API_KEY, youtube_url)
    for data in youtube_chat.get_chat():
        print(json.dumps(data['items'], indent=4))
        time.sleep(15)