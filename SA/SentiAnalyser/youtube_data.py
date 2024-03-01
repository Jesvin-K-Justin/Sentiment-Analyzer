import logging
import re
import pandas as pd
import googleapiclient.discovery 



def extract_video_id(video_url):
   
    pattern = r"(?<=v=)[a-zA-Z0-9_-]+(?=&|\?|$)"
    match = re.search(pattern, video_url)
    if match:
        return match.group(0)
    else:
        return None




def get_youtube_comments(video_url):
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return None

        api_service_name = "youtube" 
        api_version = "v3" 
        DEVELOPER_KEY = "AIzaSyAdbKxiRs1TpNuaLV4RZfVolq9SFFgLf0E" 
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY) 

        request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100) 
        response = request.execute() 

        comments = [] 
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet'] 
            comments.append([comment['authorDisplayName'], comment['publishedAt'], comment['updatedAt'], comment['likeCount'], comment['textDisplay']]) 

        df = pd.DataFrame(comments, columns=['author', 'published_at', 'updated_at', 'like_count', 'text'])

        return df

    except Exception as e:
        # Log the error using the logging module
        logging.error(f"Error occurred while retrieving YouTube comments: {str(e)}")
        return None



    
def colName1(youtube_df):
    try:
        
        try:
            possible_columns = ["text", "tweet", "comment", "comments", "feedback"]
            for col_name in possible_columns:
                youtube_df.columns = youtube_df.columns.str.lower()
                if col_name in youtube_df.columns:
                    j = col_name
                    df1 = youtube_df[[col_name]]
                    return df1, j
        except Exception as e:
            print("None of the specified columns found.")
            return None, None
    except Exception as e:
        print("Something went wrong:", e)
        return None, None