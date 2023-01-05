import pymysql
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from matplotlib import font_manager,rc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import warnings
warnings.filterwarnings('ignore')

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
        self.btn_graph.clicked.connect(self.draw_graph)
        self.btn_del.clicked.connect(self.check_del)
        self.covid_table.setColumnWidth(0, 250)  # 행의 사이즈 조절.
        self.covid_table.setColumnWidth(1, 250)
        self.covid_table.setColumnWidth(2, 225)
        self.covid_table.setColumnWidth(3, 225)
        self.covid_table.setColumnWidth(4, 235)
        self.covid_table.setColumnWidth(5, 240)
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

    def draw_graph(self):  # 그래프 그리기
        try:
            # --------------------------------------------------------------------
            # 그래프에 넣을 값 가져오기 row에 사용자가 선택한 테이블위젯의 행이 들어가 있음 ex)5번째 행을 선택했다면 5
            row = self.covid_table.currentRow()
            # select_country에 검색결과[선택행의 인덱스][국가 인덱스]를 담아줌 ex) 대한민국
            select_country = self.result[row][2]
            # select_date에 검색결과[선택행의 인덱스][날짜 인덱스]를 '-'를 기준으로 쪼개서 넣어줌 ex) ['2020','01','05']
            select_date = self.result[row][0].split('-')
            year = select_date[0]
            # year_month에 필요한 값 년-월 형식으로 넣어줌 ex)'2020-01'
            year_month = select_date[0] + '-' + select_date[1]
            # print(year_month)
            # --------------------------------------------------------------------
            # sql 데이터 가져오기
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='00000000',
                                        db='sql_dibidibidib',
                                        charset='utf8')

            self.cursor = self.conn.cursor()
            # year_month와 같은 값들의 데이터를 불러옴
            self.cursor.execute(f"SELECT * FROM covid_012 where 날짜 like '%{year_month}%'"
                                f"and 국가 = '{select_country}';")
            self.a = self.cursor.fetchall()
            self.cursor.execute(f"SELECT * FROM covid_airport5 where 날짜 like'{year}%'"
                                f"and 국가 = '{select_country}'"
                                f"or 날짜 like '2018%' and 국가 = '{select_country}';")
            self.b = self.cursor.fetchall()
            print(self.b)
            print('kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
            # 불러온 값을 self.a에 넣어줌
            # 불러온 값 확인용 출력
            # for i in range(len(self.a)):
            #     print(self.a[i])
            # 데이터 닫기
            self.conn.close()
            # --------------------------------------------------------------------
            # 폰트 설정
            font_path = "C:\\Windows\\Fonts\\gulim.ttc"
            # 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
            font = font_manager.FontProperties(fname=font_path).get_name()
            # 폰트 설정
            rc('font', family=font)
            # x,y 리스트 생성
            x = list()
            y = list()
            list_y = []  # x축 빈리스트
            list_x = []
            covid_y = []
            print(self.b)
            print('gggggggggggggggg')
            for row in self.b:  # db정보 다 읽고

                year = row[0].split('-')[0]  # data 리스트의 연도 -로 구분하고 0번째 값
                if year == '2018':  # year가 2018일때
                    list_y.append(int(row[4]))  # y리스트에 여객수를 추가
                    list_x.append(row[0].split('-')[1])  # x리스트에 날짜 추가
                else:
                    covid_y.append(int(row[4]))

            # x리스트에는 날짜를 넣고 y리스트에는 누적확진자를 넣어줌
            for i in self.a:
                x.append(i[0])
                y.append(int(i[5]))
            print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
            print(list_x)
            print('kkkkkkkkkkkkkkkkkkkkkkk')
            # 그래프 생성
            self.fig = plt.Figure()
            self.fig_2 = plt.Figure()
            self.fig_3 = plt.Figure()
            self.canvas = FigureCanvas(self.fig)
            self.canvas_2 = FigureCanvas(self.fig_2)
            self.canvas_3 = FigureCanvas(self.fig_3)
            # 그래프 초기화 그래프가 이미 들어가 있을 때 다른 그래프를 넣으면 바뀌게 해줌
            for i in range(self.graph_verticalLayout.count()):
                self.graph_verticalLayout.itemAt(i).widget().close()
                self.graph_verticalLayout_2.itemAt(i).widget().close()
                self.graph_verticalLayout_3.itemAt(i).widget().close()
            # 레이아웃에 그래프 넣어주기
            self.graph_verticalLayout.addWidget(self.canvas)
            self.graph_verticalLayout_2.addWidget(self.canvas_2)
            self.graph_verticalLayout_3.addWidget(self.canvas_3)
            # self.fig.add_subplot(x축갯수,y축갯수,몇번째 그래프) 이건 걍 그림봐야됨
            self.ax = self.fig.add_subplot(111)
            self.ax2 = self.fig_2.add_subplot(111)
            # self.ax3 = self.fig_3.add_subplot(111)
            # self.ax.tick_params(axis='x')
            # 격자 넣기 이거 같은 경우에는 y축에만 넣었음
            self.ax.grid(axis='y')
            self.ax2.grid(axis='y')

            # y축의 속성값 변경해주기 색상=빨간색 회전=45도
            self.ax.tick_params(axis='y', colors='red', rotation=45, labelsize=8)
            self.ax2.tick_params(axis='y', colors='black', rotation=45, labelsize=8)

            # 이제 그래프를 그릴 껀데 x리스트에 있는 걸 x축에 넣고, y리스트를 y축에 넣고 라벨에는 선택한 년월이 들어감
            self.ax.plot(x, y, label=f'{year_month}')
            self.ax2.plot(list_x, list_y, 'hotpink', label='2018')
            self.ax2.plot(covid_y, 'b', label=f"{year}")

            # x축의 값들이 길어서 겹쳐보이기 때문에 3개만 넣어주는거임 ex)01-03~01-31까지 있는 데이터면 01-03,01-07,01-31
            self.ax.set_xticks([0, len(x) // 2, len(x) - 1])
            # x랑 y축이 뭔지 설명해주는거
            self.ax.set_xlabel("날짜", color='gray')
            self.ax2.set_xlabel("월", color='gray')
            self.ax.set_ylabel("누적확진자", color='gray')
            self.ax2.set_ylabel("승객수", color='gray')
            current_values = self.fig_2.gca().get_yticks()
            self.fig_2.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
            self.ax2.legend()
            # 그래프의 제목
            self.ax.set_title(f'{select_country} {year_month}월 누적확진자')
            self.ax2.set_title(f'{select_country} {year}년 항공 승객수')
            # 그래프 그리기
            self.canvas.draw()
            self.canvas_2.draw()
            self.canvas_3.draw()
        except:
            pass

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

    widget.setFixedWidth(1600)
    widget.setFixedHeight(1200)
    widget.show()
    app.exec_()


