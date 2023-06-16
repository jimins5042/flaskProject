# 개요

- 교통사고 분석시스템 TAAS의 2010~2021년 교통사고 통계 데이터를 사용해 LSTM 확률 모델 생성
- Flask 프레임워크를 활용해서 확률 모델을 Rest API 형태로 구성하여 배포

# 상세
‘학교 근처의 교통사고 확률 모델 생성 및 특정 상황 및 기준에 맞는 사람에게 사고 주의 알림 전달’을 달성하기 위해, 
교통사고 데이터를 이용하여 머신러닝을 통해 확률 모델을 생성하였다.
이 모델을 배포하기 위해 Flask를 사용하여 Rest api를 개발하였다.

확률모델 배포 과정은 다음과 같다.

1. 전처리가 끝난 csv파일을 DB에 주기적으로 insert 한다.
2. DB에 저장된 데이터를 데이터프레임으로 변환한 후, 머신러닝을 진행한다.
3. Flask를 사용하여 Rest api를 생성한다.
4. 예측하고 싶은 데이터를 api를 통해 확률모델에게 전달한다.
4. 받아온 데이터에 대한 예측결과를 반환한다.


## CSV 파일 DB에 삽입

pymysql 라이브러리를 사용하여 데이터베이스와 연결하였다.

- 전처리가 끝난 csv 파일을 데이터베이스에 삽입하는 코드
~~~
#Data.py 클래스

 def insertCSV(self):
        # DB 연결
        db = pymysql.connect(host='localhost', port=3306, user='user1', passwd='', db='accident', charset='utf8')
        cursor = db.cursor()

        # csv 파일 가져오기
        df = pd.read_csv('C:/data.csv', encoding='cp949')
        df = df.fillna('')  # 빈칸이 있을 경우 빈 문자열로 대체

        # 데이터 셋의 총 행의 수, 열의 수 출력
        row_count, column_count = df.shape
        print("총 행(row) 수 : ", row_count)
        print("총 칼럼(열) 수 : ", column_count)

        # sql 구문
        # INSERT IGNORE : 기본키가 중복 될 경우(중복 데이터일 경우) 데이터 삽입 안 함
        sql = '''
        INSERT IGNORE INTO accident.accident 
        (사고번호, 사고일시, 
        요일, 시군구, 사고내용, 사망자수, 중상자수, 
        경상자수, 부상신고자수, 사고유형, 법규위반, 노면상태, 
        기상상태, 도로형태, 가해운전자_차종, 가해운전자_성별, 가해운전자_연령, 
        가해운전자_상해정도, 피해운전자_차종, 피해운전자_성별, 피해운전자_연령, 피해운전자_상해정도) 
        VALUES (
        %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s)

        '''
        # 데이터 삽입 시작
        print("CSV INSERT")

        for index, row in df.iterrows():
            values = (row['사고번호'], row['사고일시'],
                      row['요일'], row['시군구'], row['사고내용'], row['사망자수'], row['중상자수'],
                      row['경상자수'], row['부상신고자수'], row['사고유형'], row['법규위반'], row['노면상태'],
                      row['기상상태'], row['도로형태'], row['가해운전자 차종'], row['가해운전자 성별'], row['가해운전자 연령'],
                      row['가해운전자 상해정도'], row['피해운전자 차종'], row['피해운전자 성별'], row['피해운전자 연령'], row['피해운전자 상해정도']
                      )

            cursor.execute(sql, values)

        print("OK")

        # 6. DB에 Complete 하기
        db.commit()
        # 7. DB 연결 닫기
        db.close()
~~~

사용한 SQL문은 다음과 같다

INSERT IGNORE 구문 : 중복된 데이터를 무시하고 INSERT 하는 구문.
PRIMARY KEY인 ‘사고번호’ 칼럼이 이미 DB에 존재할 경우, DB에 삽입하지 않는다.



## DB에 저장된 데이터를 Dataframe으로 변환

- 데이터베이스에 삽입된 데이터셋을 조회한 뒤 데이터프레임으로 변환
~~~
def selectCSV(self):
        # DB 연결
        db = pymysql.connect(host='localhost', port=3306, user='user1', passwd='', db='accident',
                             charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        sql = "select * from accident"     #DB 조회
        cursor.execute(sql)

        # DB에서 조회한 데이터를 머신러닝하기 쉽도록 데이터프레임 형태로 변환
        data = cursor.fetchall()
        dataSet = pd.DataFrame(data)

        db.close()
        # DataFrame의 첫 몇 행을 표시
        print(dataSet.head)
        return dataSet
~~~

dataframe: 여러 타입의 데이터가 혼재된 데이터 구조
- 데이터 분석의 기본 단위인 데이터 집합 또는 데이터 행렬
- 데이터셋을 머신러닝에 활용하기 위해, 조회한 데이터를 pandas 라이브러리를 사용하여 데이터프레임 형태로 변환하였다.


![](https://velog.velcdn.com/images/2jooin1207/post/8edd90eb-46ec-4da3-932f-c1cee38ef567/image.PNG)

‘dataSet.head’로 데이터프레임으로 잘 변환되었는지 확인한 결과, 성공한 것을 볼 수 있었다.

- 머신러닝을 위한 train 데이터셋과 test 데이터셋 분리
~~~
def trainData(self):

        print("데이터셋 조회")
        dataSet = self.selectCSV()

        print("train data 분리")
        # 2010년~2021년 데이터를 훈련 데이터로 사용
        train = dataSet[dataSet['사고번호'] < '2022000000000000']
        print(train.head)

        return train

    def testData(self):
        print("데이터셋 조회")
        dataSet = self.selectCSV()

        # 2022년 데이터를 테스트 데이터로 사용
        print("test data 분리")
        test = dataSet[dataSet['사고번호'] >= '2022000000000000']
        print(test.head)
        return test
~~~

2010~2021년 데이터를 학습시킨후, 2022년 데이터셋을 통해 얼마나 잘 학습했는지 파악하기 위해 데이터셋을 분리했다.

## Flask를 이용한 rest api 생성

~~~
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
~~~

머신러닝 api를 만들기 위해 Flask를 사용하였다.
‘날씨’, ‘나이’, ‘시간대’를 받아와서 확률 모델에 전달하면, 예측 값을 반환한다.


![](https://velog.velcdn.com/images/2jooin1207/post/859e5724-6515-43e6-a9c4-0d56a887601b/image.PNG)

- 테스트용 임시 페이지를 만들어 다음과 같이 ‘날씨’, ‘나이’, ‘시간‘ 값을 확률모델에게 전달
- api는 확률모델이 반환한 예측값을 전달한다.

![](https://velog.velcdn.com/images/2jooin1207/post/440fb4c7-faee-4363-a3bf-fb959ef9c04c/image.PNG)

![](https://velog.velcdn.com/images/2jooin1207/post/b9d60e28-592e-4766-a7a5-3c2d53f8a769/image.PNG)

Postman을 사용하여 머신러닝 api 테스트
- Postman을 사용하여 테스트 해본 결과, 잘 작동하는 것을 확인했다.
- api를 개발하는 시점에는 확률모델이 완성이 되지않아 76이라는 임시값을 삽입했다.

## 주기적인 데이터 삽입 및 확률모델 재생성

~~~
#app.py

#APScheduler 라이브러리를 사용하여 주기적으로 데이터 DB에 삽입
schedule = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')

#APScheduler 실행설정, Cron방식으로, 1주-53주간실행, 일요일 4시에
#'Model.insertCSV() 메소드 실행
schedule.add_job(m.insertCSV(),'cron', week='1-53', day_of_week='6', hour='04')
schedule.start()

app = Flask(__name__)
~~~

- APScheduler 라이브러리를 사용하여 매주 일요일 4시에 데이터를 삽입하도록 설정하였다.
- CSV 파일을 특정 폴더에 넣어두면 자동으로 데이터가 DB에 삽입된다.

APScheduler 라이브러리는 특정 시간이나 주기적으로 코드를 실행시켜주는 라이브러리로, 비동기적으로 코드를 실행시킨다.
따라서 APScheduler를 통해 코드가 실행중이여도 flask서버를 통해 다른 요청을 받을 수 있다.

# 한계

![](https://velog.velcdn.com/images/2jooin1207/post/d07f4ec3-13bb-4471-9c85-575dbbc93f5c/image.PNG)

![](https://velog.velcdn.com/images/2jooin1207/post/efc4e708-dbb4-4862-ab7f-5d9cf815ff08/image.PNG)


다른 팀원이 개발한 LSTM 모델의 경우 잘 생성되었으며 시간대별, 연령대별 교통사고 발생 예측 추이를 분석할 수 있었다.
다만 시간이 부족해 주어진 특정 값들에 대한 예측값을 반환하는 것까지 구현하지 못하였다.
또 시간대별 예측값의 경우 눈에 띄게 값이 튀는 것을 볼 수 있다.


# 결론

초기 목표였던 날씨, 노면상태, 나이 등 특정 데이터를 전달하면 교통사고 확률 값을 반환하는 전북대 근방의 교통사고 확률 모델을 생성하였다. 
생성한 확률 모델을 배포하기 위해 Flask를 사용하여 머신러닝 api를 구축하였다.

이 api를 통해 조건에 부합하는 특정 사람들에게 경고 메시지를 전송하거나 교통사고 날 확률을 계산하는 사이트도 개발할 수 있는 등 다양한 활용이 가능하다.

그러나 확률모델이 처음 생각했던 것처럼 정확하지 않다는 점, 그리고 미완성 되었다는 점이 좀 아쉬웠다.

# 참고자료

- https://abluesnake.tistory.com/m/106  
- https://niceman.tistory.com/192

교통사고 비정형 데이터 분석과 LSTM을 이용한 예측 모델 개발 
- https://repository.pknu.ac.kr:8443/handle/2021.oak/1164


