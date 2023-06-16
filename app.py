from flask import Flask, render_template, request, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

from Data import Data
from Model import Model

m = Data()

#APScheduler 라이브러리를 사용하여 주기적으로 데이터 DB에 삽입
#schedule = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')

#APScheduler 실행설정, Cron방식으로, 1주-53주간실행, 일요일 4시에
#'Model.insertCSV() 메소드 실행
#schedule.add_job(m.insertCSV(),'cron', week='1-53', day_of_week='6', hour='04')
#schedule.start()

app = Flask(__name__)

# 테스트용 페이지 표시
@app.route('/')
def index():
    return render_template('index.html')


# 머신러닝 api
@app.route('/predict', methods=['POST'])
def save_data():
    data = request.form['input1']
    age = request.form['input2']
    time = request.form['input3']
    print("받아온 데이터 \n날씨 : " + data + " 나이 :" + age + " 시간대 : " + time + "시")

    # 확률 모델에 받아온 값을 전달
    model = Model()
    result = model.predict()

    print("예측결과 : " + result)

    return result


# CSV파일을 DB에 저장
@app.route('/insert')
def insert():  # put application's code here

    m = Data()
    m.insertCSV()

    return 'insert CSV'


# DB에 저장된 데이터셋 조회
@app.route('/select')
def select():  # put application's code here

    m = Data()
    m.selectCSV()

    return 'select CSV'


# DB에 저장된 데이터셋 조회
@app.route('/preprocess')
def Data_preprocessing():  # put application's code here

    m = Data()

    m.trainData()
    m.testData()

    return '데이터 전처리 테스트'


if __name__ == '__main__':
    app.run()
