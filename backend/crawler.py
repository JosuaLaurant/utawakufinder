import requests
import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY가 환경변수에 설정되지 않았습니다. .env 파일을 확인해주세요.")

def find_comment(video_id: str, max_pages=20):
    """유튜브 비디오의 댓글을 가져오는 함수"""
    comments = []
    page_token = None
    base_url = "https://www.googleapis.com/youtube/v3/commentThreads" 
    
    for _ in range(max_pages):
        params = {
            "part": "snippet",
            "videoId": video_id,
            "key": YOUTUBE_API_KEY,
            "textFormat": "plainText",
            "maxResults": 100,
        }
        if page_token:
            params["pageToken"] = page_token

        response = requests.get(base_url, params=params)    
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                raise Exception(data["error"]["message"])

            for item in data.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)

            page_token = data.get("nextPageToken")
            if not page_token:
                break
        else:
            raise Exception(f"YouTube API 오류: {response.status_code}")
    
    return comments

def extract_video_id(url): 
    """유튜브 URL에서 비디오 ID를 추출하는 함수"""
    parsed_url = urlparse(url)
    
    if parsed_url.netloc == "www.youtube.com":
        if '/live' in parsed_url.path:
            video_id = parsed_url.path.split("/")[-1] 
        else:
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get("v", [None])[0]
        return video_id
    else:
        return None