from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# 자격명 입력
name = input("삭제하고 싶은 자격명을 입력해주세요 : ")

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
# now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
service = build('calendar', 'v3', credentials=creds)

# print(now)

# Call the Calendar API
print('Getting the upcoming 100 events')
# calendarId : 캘린더 ID. primary이 자기 자신입니다. 다른 캘린더에 작성하고 싶다면 매뉴얼을 참조
# timeMin : 언제부터~ 고정값으로 2022-01-01~총100건에 대한 값을 조회
# maxResults : timeMin에서부터 긁은 데이터 중 총 100건에 대해서만 출력 100건 이상 부터는 출력 X
events_result = service.events().list(calendarId='primary',
                                      timeMin='2022-01-01T00:00:00Z',
                                      maxResults=100, singleEvents=True,
                                      orderBy='startTime').execute()
# items : events_result에서 뽑힌 list들의 모든 값
events = events_result.get('items', [])

# deleteData : 삭제될 데이터의 list 선언
deleteData = []
if not events:
    print('No upcoming events found.')

for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))

    # 삭제하고 싶은 과목명을 입력 eg) 정보처리기사라고 입력하였을 때 캘린더 제목에 정보처리기사가 포함되어 있는 것들을 아이디만 추출하여 deleteData에 삽입
    if name in event['summary']:
        print(start, event['summary'])
        deleteData.append(event['id'])

# deleteData 길이가 0이 아니라면 해당 아이디로 삭제 서비스 호출
if len(deleteData) != 0:
    for data in deleteData:
        # calendarId : 캘린더 ID. primary이 자기 자신입니다. 다른 캘린더에 작성하고 싶다면 매뉴얼을 참조
        service.events().delete(calendarId='primary', eventId=data).execute()

    print("삭제 완료")
