import pymysql
import sys
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from datetime import datetime
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from matplotlib import font_manager,rc

form_class= uic.loadUiType("covid.ui")[0]
class Covid_project(QWidget,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute('SELECT * FROM covid_012')
        self.a = self.cursor.fetchall()
        self.conn.close()
        self.header='날짜,국가코드,국가,WHO지역,신규 확진자,신규 사망자,누적 사망자'
        self.btn_add.clicked.connect(self.add_data)
        self.btn_complete.clicked.connect(self.add_data_complete)
        self.cumulative_deaths.returnPressed.connect(self.add_data_complete)
        self.btn_add_cancle.clicked.connect(self.move_main)
        self.btn_change.clicked.connect(self.change_data)
        #-------------------------------------------------------------------
        self.line_serach.returnPressed.connect(self.search)
        self.btn_search.clicked.connect(self.search)
        # self.covid_table.cellClicked.connect(self.btn_graph_able)
        self.btn_graph.clicked.connect(self.draw_graph)
        # self.btn_del.clicked.connect(self.delete_data)
        #-------------------------------------------------------------------


    def add_data(self):     # 추가를 눌렀을 때 추가페이지로 이동
        self.stackedWidget.setCurrentIndex(1)

    def move_main(self):    # 취소를 눌렀을 때 메인페이지로 이동
        self.stackedWidget.setCurrentIndex(0)

    def add_data_complete(self):    # 완료버튼 클릭시, 마지막 에디터에서 엔터를 쳤을 경우
        self.stackedWidget.setCurrentIndex(0)   # 전 스택으로 이동
        # 라인에디터 텍스트 받기-------------------------------------------------------
        date = self.date.text()
        country = self.country.text()
        new_cases = self.new_cases.text()
        cumulative_cases = self.cumulative_cases.text()
        new_deaths = self.new_deaths.text()
        cumulative_deaths = self.cumulative_deaths.text()
        # DB 추가-------------------------------------------------------------------
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            f"INSERT INTO test_covid(날짜,국가,신규확진자,누적확진자,신규사망자,누적사망자) VALUES('{date}','{country}',{int(new_cases)},{int(cumulative_cases)},{int(new_deaths)},{int(cumulative_deaths)})")
        # DB 저장
        self.conn.commit()
        # DB 닫기
        self.conn.close()
        #메시지 박스 만들어야함--------------------------------------------------------
        print('추가되었습니다. 메시지박스')
    def btn_graph_able(self):
        self.btn_graph.setEnabled(True)

    def draw_graph(self):
        row= self.covid_table.currentRow()
        print("선택된 열의 인덱스",row)
        print(row)
        select_country=self.result[row][2]
        select_date=self.result[row][0].split('-')
        year_month=select_date[0]+'-'+select_date[1]
        print(year_month)
        print(type(year_month))
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"SELECT * FROM covid_012 where 날짜 like '%{year_month}%'"
                            f"and 국가 = '{select_country}';")
        self.a = self.cursor.fetchall()
        for i in range(len(self.a)):
            print(self.a[i])
        self.conn.close()
        date_list= list()
        cumulative= list()
        font_path = "C:\\Windows\\Fonts\\gulim.ttc"
        # 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
        font = font_manager.FontProperties(fname=font_path).get_name()
        # 폰트 설정
        rc('font', family=font)
        for i in self.a:
            date_list.append(i[0])
            cumulative.append(int(i[5]))
        plt.title(f'{select_country} {year_month}월 누적확진자')
        plt.xticks([0,len(date_list)//2,len(date_list)-1])
        plt.plot(date_list,cumulative)
        plt.show()


        # self.cursor.execute(f'select * from covid_012 where 국가 = '{self.result[row][2]}'')

    def search(self):
        search_word = self.line_serach.text()
        print(search_word)
        # sql = open("yh_test_covid.sql").read()  # .sql 파일 읽음
        # self.cursor.execute(sql)
        # self.cursor.fetchall()
        # self.conn.close()
        # sql = f"SELECT * FROM `test_covid` where %{search_word}%;"
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"SELECT * FROM covid_012 where 국가 like '%{search_word}%'")
        self.result = self.cursor.fetchall()
        for i in range(len(self.result)):
            print(self.result[i])
        self.covid_table.setRowCount(len(self.result))
        Row = 0

        for k in self.result:
            self.covid_table.setItem(Row, 0, QTableWidgetItem(k[0]))         # 날짜
            self.covid_table.setItem(Row, 1, QTableWidgetItem(k[2]))         # 국가
            self.covid_table.setItem(Row, 2, QTableWidgetItem(str(k[4])))    # 신규 확진자
            self.covid_table.setItem(Row, 3, QTableWidgetItem(str(k[5])))    # 누적 확진자
            self.covid_table.setItem(Row, 4, QTableWidgetItem(str(k[6])))    # 신규 사망자
            self.covid_table.setItem(Row, 5, QTableWidgetItem(str(k[7])))    # 누적 사망자
            # self.covid_table.setItem(Row, 6, QTableWidgetItem(k[6]))
            # self.YH_main.setItem(Row, 7, QTableWidgetItem('-'))
            Row += 1
        self.conn.close()

    def change_data(self):
        self.covid_table.setEditTriggers(QAbstractItemView.AllEditTriggers)    # 테이블 위젯 수정 가능하게 변경
        data = self.result[self.covid_table.currentRow()]       # 테이블 위젯의 result 값을 data에 저장
        row = self.covid_table.selectedItems()     # 테이블 위젯의 항목 리스트 형식으로 반환된 값을 row에 저장
        date = row[0].text()       # 날짜
        country = row[1].text()    # 국가
        new_cases = row[2].text()           # 신규확진자
        cumulative_cases = row[3].text()    # 누적확진자
        new_deaths = row[4].text()          # 신규사망자
        cumulative_deaths = row[5].text()   # 누적사망자
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"UPDATE covid_012 SET 날짜='{date}' WHERE 날짜='{data[0]}'")
        self.cursor.execute(f"UPDATE covid_012 SET 국가='{country}' WHERE 국가='{data[2]}'")
        self.cursor.execute(f"UPDATE covid_012 SET 신규확진자='{new_cases}' WHERE 신규확진자='{str(data[4])}'"
                            f"and 날짜='{data[0]}' and 국가='{data[2]}'")
        self.cursor.execute(f"UPDATE covid_012 SET 누적확진자='{cumulative_cases}' WHERE 누적확진자='{str(data[5])}'"
                            f"and 날짜='{data[0]}' and 국가='{data[2]}'")
        self.cursor.execute(f"UPDATE covid_012 SET 신규사망자='{new_deaths}' WHERE 신규사망자='{str(data[6])}'"
                            f"and 날짜='{data[0]}' and 국가='{data[2]}'")
        self.cursor.execute(f"UPDATE covid_012 SET 누적사망자='{cumulative_deaths}' WHERE 누적사망자='{str(data[7])}'"
                            f"and 날짜='{data[0]}' and 국가='{data[2]}'")
        self.conn.commit()
        self.conn.close()

    # def delete_data(self):


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    covid_project = Covid_project()
    widget.addWidget(covid_project)

    widget.setFixedWidth(1200)
    widget.setFixedHeight(900)
    widget.show()
    app.exec_()


