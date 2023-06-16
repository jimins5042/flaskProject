import pymysql.cursors
import pandas as pd


class Data:

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
        # insertDB 메소드 종료

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




