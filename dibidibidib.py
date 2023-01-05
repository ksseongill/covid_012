import pymysql
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from matplotlib import font_manager,rc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

form_class = uic.loadUiType("covid.ui")[0]
class Covid_project(QWidget,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(0)
        self.btn_add.clicked.connect(self.move_add_data)
        self.btn_complete.clicked.connect(self.check_add)
        self.cumulative_deaths.returnPressed.connect(self.check_add)
        self.btn_add_cancle.clicked.connect(self.move_main)
        self.btn_change.clicked.connect(self.check_change)
        #-------------------------------------------------------------------
        self.line_serach.returnPressed.connect(self.search)
        self.btn_search.clicked.connect(self.search)
        self.covid_table.cellClicked.connect(self.btn_enable)
        self.btn_graph.clicked.connect(self.draw_graph)
        self.btn_del.clicked.connect(self.check_del)
        #-------------------------------------------------------------------

    def move_add_data(self):     # 추가를 눌렀을 때 추가페이지로 이동
        self.stackedWidget.setCurrentIndex(1)

    def move_main(self):    # 취소를 눌렀을 때 메인페이지로 이동
        self.stackedWidget.setCurrentIndex(0)
        self.le_clear()

    def le_clear(self):
        self.date.clear()
        self.country.clear()
        self.new_cases.clear()
        self.new_deaths.clear()
        self.cumulative_cases.clear()
        self.cumulative_deaths.clear()
    def check_add(self):    # 추가 재확인
        ck_add = QMessageBox.question(self, '추가', '추가 하시겠습니까?', QMessageBox.Yes | QMessageBox.No)
        if ck_add == QMessageBox.Yes:
            self.add_data_complete()
        else: # 라인에디터 클리어
            self.le_clear()
    def add_data_complete(self):    # 완료버튼 클릭시, 마지막 에디터에서 엔터를 쳤을 경우
        try:
            # 라인에디터 텍스트 받기-------------------------------------------------------
            date = self.date.text()
            country = self.country.text()
            new_cases = self.new_cases.text()
            cumulative_cases = self.cumulative_cases.text()
            new_deaths = self.new_deaths.text()
            cumulative_deaths = self.cumulative_deaths.text()
            if date=='' or country=='':
                QMessageBox.information(self, '추가', '날짜와 국가는 필수항목입니다.')
                return
            # DB 추가-------------------------------------------------------------------
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                                   charset='utf8')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                f"INSERT INTO covid_012(날짜,국가,신규확진자,누적확진자,신규사망자,누적사망자) VALUES('{date}','{country}',{int(new_cases)},{int(cumulative_cases)},{int(new_deaths)},{int(cumulative_deaths)})")
            # DB 저장
            self.conn.commit()
            # DB 닫기
            self.conn.close()
            QMessageBox.information(self, '추가',  f"날짜:{date}\n국가:{country}\n신규확진자:{int(new_cases)}\n누적확진자:{int(cumulative_cases)}\n"
                                                 f"신규사망자:{int(new_deaths)}\n누적사망자:{int(cumulative_deaths)}\n추가되었습니다")
            self.stackedWidget.setCurrentIndex(0)   # 전 스택으로 이동
        except: self.stackedWidget.setCurrentIndex(0)   # 전 스택으로 이동
    def btn_enable(self):   # 테이블위젯의 셀 클릭 했을 때 버튼 활성화 시키기
        self.btn_graph.setEnabled(True)
        self.btn_change.setEnabled(True)
        self.btn_del.setEnabled(True)
    def draw_graph(self):   # 그래프 그리기
        try :
            # --------------------------------------------------------------------
            # 그래프에 넣을 값 가져오기
            row= self.covid_table.currentRow()
            print(row)
            select_country=self.result[row][2]
            select_date=self.result[row][0].split('-')
            year_month=select_date[0]+'-'+select_date[1]
            print(year_month)
            # --------------------------------------------------------------------
            # sql 데이터 가져오기
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                                   charset='utf8')
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"SELECT * FROM covid_012 where 날짜 like '%{year_month}%'"
                                f"and 국가 = '{select_country}';")
            self.a = self.cursor.fetchall()
            for i in range(len(self.a)):
                print(self.a[i])
            self.conn.close()
            # --------------------------------------------------------------------
            # 폰트 설정
            font_path = "C:\\Windows\\Fonts\\gulim.ttc"
            # 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
            font = font_manager.FontProperties(fname=font_path).get_name()
            # 폰트 설정
            rc('font', family=font)
            x= list()
            y= list()
            for i in self.a:
                x.append(i[0])
                y.append(int(i[5]))
            self.fig = plt.Figure()
            self.canvas = FigureCanvas(self.fig)
            # 그래프 초기화
            for i in range(self.graph_verticalLayout.count()):
                self.graph_verticalLayout.itemAt(i).widget().close()
            self.graph_verticalLayout.addWidget(self.canvas)
            self.ax = self.fig.add_subplot(111)
            # self.ax.tick_params(axis='x')
            self.ax.grid(axis='y')
            self.ax.tick_params(axis='y', colors='red',rotation=45)
            self.ax.plot(x, y, label=f'{year_month}')
            self.ax.set_xticks([0,len(x)//2,len(x)-1])
            self.ax.set_xlabel("날짜",color='gray')
            self.ax.set_ylabel("누적확진자",color='gray')
            self.ax.set_title(f'{select_country} {year_month}월 누적확진자')
            self.canvas.draw()
        except: pass



    def search(self):
        self.search_word = self.line_serach.text()
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                               charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"SELECT * FROM covid_012 where 국가 like '%{self.search_word}%'"
                            f"and 삭제여부 = '0' order by 국가 and 날짜")

        self.result = self.cursor.fetchall()
        # 검색결과 없을때
        if self.result==():
            QMessageBox.information(self, '검색', f'{self.search_word}에 대한 검색결과가 없습니다.')
            return
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
            Row += 1
        self.conn.close()
    def check_change(self): # 수정 재확인
        if self.covid_table.currentRow()== -1:
            QMessageBox.information(self, '수정', '선택된 값이 없습니다.')
            return
        self.data = self.result[self.covid_table.currentRow()]  # 테이블 위젯의 result 값을 data에 저장
        self.row = self.covid_table.selectedItems()        # 테이블 위젯의 항목 리스트 형식으로 반환된 값을 row에 저장
        self.date = self.row[0].text()  # 날짜
        self.country = self.row[1].text()  # 국가
        self.new_cases = self.row[2].text()  # 신규확진자
        self.cumulative_cases = self.row[3].text()  # 누적확진자
        self.new_deaths = self.row[4].text()  # 신규사망자
        self.cumulative_deaths = self.row[5].text()  # 누적사망자
        if self.data[0] != self.date or self.data[2] != self.country:
                QMessageBox.information(self, '수정', '날짜와 국가는 수정 할 수 없습니다.')
                self.search()
                return
        elif self.data[4:-1] == (int(self.new_cases),int(self.cumulative_cases),int(self.new_deaths),int(self.cumulative_deaths)):
            QMessageBox.information(self, '수정', '수정된 값이 없습니다.')
        else:
            ck_chage = QMessageBox.question(self, '수정', '수정 하시겠습니까?', QMessageBox.Yes | QMessageBox.No, )
            if ck_chage == QMessageBox.Yes:
                self.change_data()
            else: return
    def change_data(self):
        try:
            self.covid_table.setEditTriggers(QAbstractItemView.AllEditTriggers)    # 테이블 위젯 수정 가능하게 변경

            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                                   charset='utf8')
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"UPDATE covid_012 SET 신규확진자='{self.new_cases}', 누적확진자='{self.cumulative_cases}', 신규사망자='{self.new_deaths}', 누적사망자='{self.cumulative_deaths}'"
                                f"where 날짜='{self.data[0]}' and 국가='{self.data[2]}'")
            self.conn.commit()
            self.conn.close()
            QMessageBox.information(self, '수정', '수정되었습니다.')
        except: pass

    def check_del(self): # 삭제 재확인
        if self.covid_table.currentRow()== -1:
            QMessageBox.information(self, '삭제', '선택된 값이 없습니다.')
            return
        ck_del = QMessageBox.question(self, '삭제', '삭제 하시겠습니까?', QMessageBox.Yes | QMessageBox.No)
        if ck_del == QMessageBox.Yes:
            self.delete_data()
    def delete_data(self):
        try:
            self.data = self.result[self.covid_table.currentRow()]  # 테이블 위젯의 result 값을 data에 저장
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000', db='sql_dibidibidib',
                                        charset='utf8')
            self.cursor = self.conn.cursor()
            self.cursor.execute(
                f"UPDATE covid_012 SET 삭제여부= CONCAT ('1')"
                f"where 날짜='{self.data[0]}' and 국가='{self.data[2]}'")
            self.conn.commit()
            self.conn.close()
            QMessageBox.information(self, '삭제','삭제되었습니다.')
        except: return


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    covid_project = Covid_project()
    widget.addWidget(covid_project)

    widget.setFixedWidth(1200)
    widget.setFixedHeight(900)
    widget.show()
    app.exec_()


