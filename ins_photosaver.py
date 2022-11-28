import os
import requests
import pandas as pd
import datetime
from time import sleep
import random
from fake_useragent import UserAgent
import re
from tqdm import tqdm,trange
import emoji
import urllib.request
from jsonpath import jsonpath

#set database fields
page_list = []
id_list = []
text_list = []
time_list = []
like_count_list = []
comment_count_list = []
photo_url_list = []


#Set the file name to the date and time of the tweet (Japan time)
def change_name(date):
    date_modify = re.sub("\:| ", "", date)
    return date_modify

#Delete emoji in tweets
def remove_emoji(src_str):
    noemoji = ''.join(c for c in src_str if c not in emoji.EMOJI_DATA)
    newtext =  re.sub("\n", "", noemoji)
#    newtext1 =  re.sub(r'http\S+', "", newtext)
    return newtext

#Create a folder for each user function
def makeDIR(name):
            document_path = os.path.abspath('.') + "/Result"
            path = document_path+"/"+name
            if not os.path.exists(path):
                os.mkdir(path)
            os.chdir(path)


def get_insPhoto(user_ids, csv_file, max_pages):

    for user_id in user_ids:

        m = 0
        max_id = '0'
        dir=os.path.abspath('.')+'/'

        for page in trange(1,max_pages + 1):
                    wait_senconds = random.uniform(0, 1)
                    print('Start waiting for {} seconds'.format(wait_senconds))
                    sleep(wait_senconds)
                    print('Start scraping for page {}'.format(page))
                    if page == 1:
                        url = 'https://www.instagram.com/api/v1/feed/user/{}/?count=12'.format(user_id)
                    else:
                        if max_id == '0':
                            print('next_max_id is 0, break now')
                            break
                        url = 'https://www.instagram.com/api/v1/feed/user/{}/?count=12&max_id={}'.format(user_id,max_id)

                    ua = UserAgent(verify_ssl=False)
                    #please copy your own browes header info. chrome maybe the better choice.
                    headers = {
                        "user-agent": ua.random,
                        "cookie": "XXXXXXXXXX",
                        "accept": "XXXXXXXXXX",
                        "accept-encoding": "XXXXXXXXXX",
                        "x-ig-app-id": "XXXXXXXXXX",
                        "x-requested-with": "XXXXXXXXXX"                    
                                }

                    r = requests.get(url, headers = headers)
                    print(r.status_code)     #200 is corrent
                    #last page which have no maxId
                    try:
                        max_id = r.json()["next_max_id"]
                    except KeyError:
                        max_id = '0'
                    photos = r.json()["items"]
                    # get the post infomation
                    for photo in photos:
                        # if post have no caption set element a meplty values
                        if photo['caption'] is None: 
                            id_list.append("None")
                            text_list.append("None")
                            time_list.append("None")
                        else:
                            id_list.append(photo['caption']['media_id'])
                            #change unixTime to human time
                            unix_time = photo['taken_at']
                            date_time = datetime.datetime.fromtimestamp(unix_time)
                            time_list.append(date_time.strftime('%Y-%m-%d %H:%M:%S'))
                            emoji_text = re.sub("\n", "", photo['caption']['text'])
                            newtext = remove_emoji(emoji_text)
                            text_list.append(newtext)
                        like_count_list.append(photo['like_count'])
                        comment_count_list.append(photo['comment_count'])
                        try:
                            photo_url_list.append(photo['image_versions2']['candidates'][0]['url'])
                            photo_url = photo['image_versions2']['candidates'][0]['url']
                            # print(photo_url)
                            urllib.request.urlretrieve(photo_url,dir + date_time.strftime('%Y%m%d_%H%M%S') + str(m) + ".jpg")
                            print('Downloading picture of No.' + str(m))
                            m = m + 1
                        except KeyError:
                            photo_url_list.append(photo['carousel_media'][0]['image_versions2']['candidates'][0]['url'])
                            photos = photo['carousel_media']
                            for i in photos:
                                photo_url = i['image_versions2']['candidates'][0]['url']
                                # print(photo_url)
                                urllib.request.urlretrieve(photo_url,dir + date_time.strftime('%Y%m%d_%H%M%S') + str(m) + ".jpg")
                                print('Downloading picture of No.' + str(m))
                                m = m + 1                

        df = pd.DataFrame(
            {
                'MediaId': id_list,
                'PostTime': time_list,
                'PostText': text_list,
                'LikeCount': like_count_list,
                'CommentCount': comment_count_list,
                'PicsUrl': photo_url_list
            }
        )
        print(df)
        print('Task Complete!!!')

        if os.path.exists(file_name):
            header = False
        else:
            header = True
        #save csv file
        df.to_csv(dir + file_name, mode='a+',index=False, header=header, encoding='utf-8-sig')
        print('Result file saved succefuly! {}'.format(file_name))

if __name__ == '__main__':
    ins_user_id = ['00000000000000',] #get the instagram user id
    max_page = 00   #input how many pages you want to scrape
    csv_file = "XXXX"  #file name

    #create the folder
    makeDIR(csv_file)

    file_name = csv_file + ".csv"
    #if exist delete file first
    if os.path.exists(file_name):
        print('csv file already exits,delete first:', file_name)
        os.remove(file_name)
    # Run function
    get_insPhoto(user_ids=ins_user_id, csv_file=csv_file, max_pages= max_page)
