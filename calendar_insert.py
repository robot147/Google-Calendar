from bs4 import BeautifulSoup
from urllib.request import urlopen
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import json
import datetime
import os.path

# 자격명 입력
name = input("추가하고 싶은 자격명을 입력해주세요 : ")
jmCd = ""

with open('licenselist.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

list = json.loads(json.dumps(json_data, ensure_ascii=False))

if name in list:
    jmCd = list[name]
else:
    print("자격명을 확인하여 다시 입력해주세요.")

# BeautifulSoup을 이용한 웹 크롤링 / jmCd는 자격명에 대한 각각의 고유값
response = urlopen('https://www.q-net.or.kr/crf005.do?id=crf00503s02&gSite=Q&gId=&jmCd=' + jmCd)
soup = BeautifulSoup(response, 'html.parser')
result = []
list = ["필기 원서 접수", "필기 시험", "필기 합격", "실기 원서 접수", "실기 시험", "실기 합격"]

def key(index, data):
    if index == 0:
        dic["회차"] = data.split()[len(data.split())-1]
    elif index == 1:
        dic["필기 원서 접수"] = data
    elif index == 2 :
        dic["필기 시험"] = data
    elif index == 3 :
        dic["필기 합격"] = data
    elif index == 4 :
        dic["실기 원서 접수"] = data.split()[0]
    elif index == 5 :
        dic["실기 시험"] = data
    elif index == 6 :
        dic["실기 합격"] = data

# 구글 캘린더에서는 날짜를 "-"로 써줘야함. eg) 2022-01-01
for data in soup.select(".tbl_normal table tbody > tr"):
    dic = {}
    str = ""
    for index in range(0, len(data.select("td"))):
        if "~" in data.select("td")[index].get_text().strip().split():
            for i in range(0, len(data.select("td")[index].get_text().strip().split())):
                str += data.select("td")[index].get_text().strip().split()[i]
                key(index, str.replace(".", "-"))
        else:
            key(index, data.select("td")[index].get_text().strip().replace(".", "-"))
    result.append(dic)

# 구글 계정 인증 절차
# from_client_secrets_file 함수를 통하여 OAuth JSON 파일로 token.json를 만들어 줍니다.
# json 파일 위치는 해당 py 파일과 같은 디렉토리에 넣으시면 됩니다.
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

"""Shows basic usage of the Google Calendar API.
Prints the start and name of the next 10 events on the user's calendar.
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.

# 기존에 token.json 파일이 있다면 기존 파일을 참조
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

print("구글 계정 인증 완료")

# 서비스 객체 생성 및 시간 지정
now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
service = build('calendar', 'v3', credentials=creds)

print(now)

# 캘린더에 추가할 파라미터 생성 및 서비스 객체를 이용한 캘린더 추가
for data in result:
    for val in list:
        calendarData = {
            'summary': name + " " + data['회차'] + " " + val,  # 일정 제목
            # 'location': '서울특별시 성북구 정릉동 정릉로 77', # 일정 장소
            'description': name + " " + data['회차'] + " " + val,  # 일정 설명
            'start': {  # 시작 날짜 (몇시부터~ 일정을 넣고 싶으면 아래 dateTime으로 설정)
                #     # 'dateTime': now, # 완
                #     'dateTime': '2022-04-22T09:00:00',
                # 'date' : '2022-04-24'
                'timeZone': 'Asia/Seoul',
                'date': data[val] if len(data[val].split("~")) == 1 else data[val].split("~")[0] # 하루 종일
            },
            'end': {  # 종료 날짜 (~몇시까지 일정을 넣고 싶으면 아래 dateTime으로 설정)
                # 'dateTime': now + 'T10:00:00',
                # 'dateTime': now, # 완
                # 'dateTime': '2022-04-25T10:00:00',
                'timeZone': 'Asia/Seoul',
                'date': data[val] if len(data[val].split("~")) == 1 else data[val].split("~")[1] # 하루 종일
            },
            # 'recurrence': [ # 반복 지정
            #     'RRULE:FREQ=DAILY;COUNT=2' # 일단위; 총 2번 반복
            # ],
            # 'attendees': [ # 참석자
            #     {'email': 'lpage@example.com'},
            #     {'email': 'sbrin@example.com'},
            # ],
            'transparency': 'transparent',
            'reminders': {  # 알림 설정
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 15 * 60},  # 24 * 60분 = 하루 전 알림 / 15 * 60 = 하루 전 오전 9시에 알림
                    {'method': 'popup', 'minutes': 15 * 60},  # 핸드폰 팝업으로 뜨게 됩니다.
                ],
            },
        }

        # calendarId : 캘린더 ID. primary이 자기 자신입니다. 다른 캘린더에 작성하고 싶다면 매뉴얼을 참조
        event = service.events().insert(calendarId='primary',
                                        body=calendarData).execute()

        print("Calendar Name : " + event['summary'] + ", Calendar Link : " + event['htmlLink'])

        print("캘린더 추가 완료")