#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import time
import ex1_kwstest as kws
import ex2_getVoice2Text as gv2t
import ex4_getText2VoiceStream as tts
import MicrophoneStream as MS

import requests, json

with open('./sidoCityName.json') as json_file:
    json_data = json.load(json_file)
    state_data = json_data['StateData']
    city_data = json_data['CityData']

def getDustInfo(State ,City):
     ServiceKey = "사용자의 API키를 입력해 주세요"
     url = 'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getCtprvnMesureSidoLIst?serviceKey={}&numOfRows=40&pageNo=1&sidoName={}&searchCondition=HOUR&_returnType=json'.format(ServiceKey, State)
     data = requests.get(url).json()
     for result_data in data['list']:
         if(result_data['cityName'] == City) :
            pm25Value = result_data['pm25Value']
            pm10Value = result_data['pm10Value']
            print(result_data['cityName'])
            if pm10Value != '' and pm25Value !='':
                pm25_status, pm10_status = getDustStanardInfo(int(result_data['pm25Value']), int(result_data['pm10Value']))
                return_data = "현재 " + State + City + "의 미세먼지는 초미세먼지 " +  str(result_data['pm25Value']) + " 마이크로그램으로 " + pm25_status + " 단계이며 미세먼지는 " + str(result_data['pm10Value']) + " 마이크로그램으로 " + pm10_status + " 단계 입니다."
                print(return_data)
            elif pm10Value == '':
                pm25_status, pm10_status = getDustStanardInfo(int(result_data['pm25Value']), 10)
                return_data = "현재 " + State + City + "의 미세먼지는 초미세먼지 " +  str(result_data['pm25Value']) + " 마이크로그램으로 " + pm25_status + " 단계이고 미세먼지는 측정중 입니다."
                print(return_data)
            elif pm25Value == '':
                pm25_status, pm10_status = getDustStanardInfo(10, int(result_data['pm10Value']))
                return_data = "현재 " + State + City + "의 미세먼지는 미세먼지는 " + str(result_data['pm10Value']) + " 마이크로그램으로 " + pm10_status + " 단계이고 초미세먼지는 측정중 입니다."
                print(return_data)
            return(return_data)

def getDustStanardInfo(pm25, pm10):
    pm10_status = ''
    pm25_status = ''
    if( 0 < pm10 and pm10 <= 30):
        pm10_status = '좋음'
    elif(30 < pm10 and pm10 <= 80):
        pm10_status = '보통'
    elif(80 < pm10 and pm10 <= 150):
        pm10_status = '나쁨'
    else:
        pm10_status = '매우 나쁨'

    if( 0 < pm25 and pm25 <= 15):
        pm25_status = '좋음'
    elif(15 < pm25 and pm25 <= 35):
        pm25_status = '보통'
    elif(35 < pm25 and pm25 <= 75):
        pm25_status = '나쁨'
    else:
        pm25_status = '매우 나쁨'

    return(pm25_status, pm10_status)


def findCity(result_text):
    find_state = ''
    find_city = ''
    find_state_status = 0
    find_city_status = 0

    for state_list in state_data:
        if result_text.find(state_list) >= 0:
            find_state = state_list
            find_state_status = 1
            for city_list in city_data[state_data[state_list]]:
                if result_text.find(city_list) >= 0:
                    find_city =  city_list
                    find_city_status = 1

    return(find_state, find_city,find_state_status, find_city_status)

def main():
    KWSID = ['기가지니', '지니야', '친구야', '자기야']
    tts_text = ''
    while 1:
        recog=kws.test(KWSID[0])
        if recog == 200:
            print('KWS Dectected ...\n Start STT...')
            text = gv2t.getVoice2Text()
            print('Recognized Text: '+ text)
            if text.find("미세 먼지 알려줘") >= 0 or text.find("미세 먼지") >= 0 :
                print("Command Detected")
                find_state, find_city, find_state_status, find_city_status= findCity(text)
                print(find_state_status,"/", find_city_status)
                if (find_state_status == 1 and find_city_status == 1):
                    print(find_state, "/", find_city)
                    tts_text = getDustInfo(find_state, find_city)
                elif(find_state_status == 1 and find_city_status == 0):
                    tts_text = "정확한 시 군 구 명을 알려주세요"
                elif(find_state_status == 0):
                    tts_text = "정확한 도 시 명을 알려주세요"
                else:
                    tts_text = "정확한 명령을 내려주세요"
            else:
                tts_text = "정확한 명령을 내려주세요"

            tts_result = tts.getText2VoiceStream(tts_text, "result_mesg.wav")
            MS.play_file("result_mesg.wav")

            time.sleep(2)
        else:
            print('KWS Not Dectected ...')

if __name__ == '__main__':
    main()

