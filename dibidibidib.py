import pymysql
import sys
import csv
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from datetime import datetime
import time

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
        # self.btn_graph.clicked.connect(self.draw_graph)
        # self.btn_del.clicked.connect(self.삭제클릭)
        #-------------------------------------------------------------------


    def add_data(self):     # 추가를 눌렀을 때 추가페이지로 이동
        self.stackedWidget.setCurrentIndex(1)

    def move_main(self):    # 취소를 눌렀을 때 메인페이지로 이동
        self.stackedWidget.setCurrentIndex(0)

    def add_data_complete(self):    # 완료버튼 클릭시, 마지막 에디터에서 엔터를 쳤을 경우
        self.stackedWidget.setCurrentIndex(0)   # 전 스택으로 이동
        # 라인에디터 텍스트 받기-------------------------------------------------------
        date= self.date.text()
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
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute('SELECT * FROM covid_012')
        self.a = self.cursor.fetchall()
        when = self.result[row][0]
        print(when)
        when_format= '%y-%m-%d'
        graph_month= datetime.strptime(when, when_format)
        print(graph_month)
        print(when)
        self.conn.close()

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
        self.covid_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        data = self.result[self.covid_table.currentRow()]
        row = self.covid_table.selectedItems()
        date = row[0].text()
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"UPDATE covid_012 SET 날짜='{date}' WHERE 날짜='{data[0]}'")
        self.conn.commit()
        self.conn.close()




if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    covid_project = Covid_project()
    widget.addWidget(covid_project)

    widget.setFixedWidth(1200)
    widget.setFixedHeight(900)
    widget.show()
    app.exec_()


