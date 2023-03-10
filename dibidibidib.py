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
        self.line_serach.returnPressed.connect(self.search)
        self.btn_search.clicked.connect(self.search)
        self.btn_graph.clicked.connect(self.draw_graph)
        self.btn_del.clicked.connect(self.check_del)
        #-------------------------------------------------------------------
        self.covid_table.setColumnWidth(0, 233)  # 행의 사이즈 조절.
        self.covid_table.setColumnWidth(1, 233)
        self.covid_table.setColumnWidth(2, 233)
        self.covid_table.setColumnWidth(3, 234)
        self.covid_table.setColumnWidth(4, 233)
        self.covid_table.setColumnWidth(5, 210)
        #-------------------------------------------------------------------

    # 추가 페이지로 이동
    def move_add_data(self):     # 추가를 눌렀을 때 추가페이지로 이동
        self.stackedWidget.setCurrentIndex(1)
    # 메인페이지로 이동
    def move_main(self):    # 취소를 눌렀을 때 메인페이지로 이동
        self.stackedWidget.setCurrentIndex(0)
        self.le_clear()
    # 추가 lineedit 클리어
    def le_clear(self):
        self.date.clear()
        self.country.clear()
        self.new_cases.clear()
        self.new_deaths.clear()
        self.cumulative_cases.clear()
        self.cumulative_deaths.clear()
    # 추가 재확인
    def check_add(self):
        ck_add = QMessageBox.question(self, '추가', '추가 하시겠습니까?', QMessageBox.Yes | QMessageBox.No)
        if ck_add == QMessageBox.Yes:
            self.add_data_complete()
        else: # 라인에디터 클리어
            self.le_clear()
    # 추가항목 데이터 업로드
    def add_data_complete(self):    # 완료버튼 클릭시, 마지막 에디터에서 엔터를 쳤을 경우
        try:
            # 라인에디터 텍스트 받기
            date = self.date.text()
            country = self.country.text()
            new_cases = self.new_cases.text()
            cumulative_cases = self.cumulative_cases.text()
            new_deaths = self.new_deaths.text()
            cumulative_deaths = self.cumulative_deaths.text()
            if date=='' or country=='':
                QMessageBox.information(self, '추가', '날짜와 국가는 필수항목입니다.')
                return
            # DB 추가
            conn = pymysql.connect(host='10.10.21.101', port=3306, user='test1', password='0000', db='sql_dibidibidib',
                                   charset='utf8')
            cursor = conn.cursor()
            # 데이터 추가하기
            cursor.execute(
                f"INSERT INTO covid_012(날짜,국가,신규확진자,누적확진자,신규사망자,누적사망자) VALUES('{date}','{country}',{int(new_cases)},{int(cumulative_cases)},{int(new_deaths)},{int(cumulative_deaths)})")
            # DB 저장
            conn.commit()
            # DB 닫기
            conn.close()
            # 추가한 값과 추가결과 보여주는 메시지박스
            QMessageBox.information(self, '추가',  f"날짜:{date}\n국가:{country}\n신규확진자:{int(new_cases)}\n누적확진자:{int(cumulative_cases)}\n"
                                                 f"신규사망자:{int(new_deaths)}\n누적사망자:{int(cumulative_deaths)}\n추가되었습니다")
            self.stackedWidget.setCurrentIndex(0)   # 전 스택으로 이동
        except: self.stackedWidget.setCurrentIndex(0)   # 전 스택으로 이동
    # 그래프 그리기
    def draw_graph(self):
        try:
            # 그래프에 넣을 값 가져오기 row에 사용자가 선택한 테이블위젯의 행이 들어가 있음 ex)5번째 행을 선택했다면 5
            row = self.covid_table.currentRow()
            # select_country에 검색결과[선택행의 인덱스][국가 인덱스]를 담아줌 ex) 대한민국
            select_country = self.result[row][2]
            # select_date에 검색결과[선택행의 인덱스][날짜 인덱스]를 '-'를 기준으로 쪼개서 넣어줌 ex) ['2020','01','05']
            select_date = self.result[row][0].split('-')
            # year 에 년도를 넣어줌 ex)'2020'
            year = select_date[0]
            # year_month에 필요한 값 년-월 형식으로 넣어줌 ex)'2020-01'
            year_month = select_date[0] + '-' + select_date[1]
            # sql 데이터 가져오기
            conn = pymysql.connect(host='10.10.21.101', port=3306, user='test1', password='0000', db='sql_dibidibidib',
                                   charset='utf8')

            cursor = conn.cursor()
            # 사용자가 선택한 값과 같은 데이터를 불러옴
            cursor.execute(f"SELECT * FROM covid_012 where 날짜 like '%{year_month}%'"
                                f"and 국가 = '{select_country}';")
            a = cursor.fetchall()
            cursor.execute(f"SELECT * FROM covid_airport where 날짜 like'{year}%'"
                                f"and 국가 = '{select_country}'"
                                f"or 날짜 like '2018%' and 국가 = '{select_country}';")
            b = cursor.fetchall()
            cursor.execute(f"SELECT * FROM dutyfree where 구분 like '합계'")
            c = cursor.fetchone()
            # 헤더 리스트 생성 (dutyfree 테이블만 열과 행이 바뀌어서 헤더값을 코드에서 선언해줌)
            header = ['구분', '2019년 01', '2019년 02', '2019년 03', '2019년 04', '2019년 05', '2019년 06',
                      '2019년 07', '2019년 08', '2019년 09', '2019년 10', '2019년 11', '2019년 12',
                      '2020년 01', '2020년 02', '2020년 03', '2020년 04', '2020년 05', '2020년 06',
                      '2020년 07', '2020년 08', '2020년 09', '2020년 10', '2020년 11', '2020년 12',
                      '2021년 01', '2021년 02', '2021년 03', '2021년 04', '2021년 05', '2021년 06',
                      '2021년 07', '2021년 08', '2021년 09', '2021년 10', '2021년 11', '2021년 12',
                      '2022년 01', '2022년 02', '2022년 03', '2022년 04', '2022년 05', '2022년 06', '2022년 07']
            # 데이터 닫기
            conn.close()
            # --------------------------------------------------------------------
            # 폰트 설정
            font_path = "C:\\Windows\\Fonts\\gulim.ttc"
            # 폰트 패스를 통해 폰트 세팅해 폰트 이름 반환받아 font 변수에 삽입
            font = font_manager.FontProperties(fname=font_path).get_name()
            # 폰트 설정
            rc('font', family=font)
            # x,y 리스트 생성
            x = []
            y = []
            list_y = []
            list_x = []
            covid_y = []
            duty_x = []
            duty_y = []
            duty_y2 = []
            # 데이터 날짜 값에서 년, 월, 일 쪼개기
            for row in b:
                year = row[0].split('-')[0]  # data 리스트의 연도 -로 구분하고 0번째 값
                if year == '2018':  # year가 2018일때
                    list_y.append(int(row[4]))  # y리스트에 여객수를 추가
                    list_x.append(row[0].split('-')[1])  # x리스트에 날짜 추가
                else:
                    covid_y.append(int(row[4]))

            for i in header:
                if '2019' in i:
                    duty_x.append(i.replace('2019년 ', ''))
            for i in c[:13]:
                if i != '합계':
                    duty_y.append(i)
            if year == '2019':
                pass
            elif year == '2020':
                for i in c[13:25]:
                    if i != '합계':
                        duty_y2.append(i)
            elif year == '2021':
                for i in c[25:36]:
                    if i != '합계':
                        duty_y2.append(i)
            elif year == '2022':
                for i in c[36:]:
                    if i != '합계':
                        duty_y2.append(i)

            # x리스트에는 날짜를 넣고 y리스트에는 누적확진자를 넣어줌
            for i in a:
                x.append(i[0])
                y.append(int(i[5]))
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
            self.ax = self.fig.add_subplot(111)
            self.ax2 = self.fig_2.add_subplot(111)
            self.ax3 = self.fig_3.add_subplot(111)
            # 격자 넣기 이거 같은 경우에는 y축에만 넣었음
            self.ax.grid(axis='y')
            self.ax2.grid(axis='y')
            self.ax3.grid(axis='y')

            # y축의 속성값 변경해주기 색상=빨간색 회전=45도
            self.ax.tick_params(axis='y', colors='black', rotation=45, labelsize=8)
            self.ax2.tick_params(axis='y', colors='black', rotation=45, labelsize=8)
            self.ax3.tick_params(axis='y', colors='black', rotation=45, labelsize=8)

            # 이제 그래프를 그릴 껀데 x리스트에 있는 걸 x축에 넣고, y리스트를 y축에 넣고 라벨에는 선택한 년월이 들어감
            self.ax.plot(x, y, label=f'{year_month}')
            self.ax2.plot(list_x, list_y, 'hotpink', label='2018')
            self.ax2.plot(covid_y, 'b', label=f"{year}")
            self.ax3.plot(duty_x, duty_y, 'hotpink', label='2019')
            self.ax3.plot(duty_y2, 'b', label=f"{year}")

            # x축의 값들이 길어서 겹쳐보이기 때문에 3개만 넣어주는거임 ex)01-03~01-31까지 있는 데이터면 01-03,01-07,01-31
            self.ax.set_xticks([0, len(x) // 2, len(x) - 1])
            # x랑 y축이 뭔지 설명해주는거
            self.ax.set_xlabel("날짜", color='gray')
            self.ax2.set_xlabel("월", color='gray')
            self.ax3.set_xlabel("월", color='gray')
            # 천단위 콤마 삽입 코드
            current_values_1 = self.fig.gca().get_yticks()
            current_values_2 = self.fig_2.gca().get_yticks()
            current_values_3 = self.fig_3.gca().get_yticks()
            self.fig.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values_1])
            self.fig_2.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values_2])
            self.fig_3.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values_3])
            # 범례 띄우기
            self.ax2.legend()
            self.ax3.legend()
            # 그래프 타이틀 설정
            self.ax.set_title(f'{select_country} {year_month}월 누적확진자')
            self.ax2.set_title(f'{select_country} {year}년 항공 승객수')
            self.ax3.set_title(f'{year}년 공항 면세 총 매출액')
            # 그래프 그리기
            self.canvas.draw()
            self.canvas_2.draw()
            self.canvas_3.draw()
        except:
            pass
    # 검색 메서드 및 검색결과 메시지 박스
    def search(self):
        # 검색어 받기
        self.search_word = self.line_serach.text()
        conn = pymysql.connect(host='10.10.21.101', port=3306, user='test1', password='0000', db='sql_dibidibidib',
                               charset='utf8')
        cursor = conn.cursor()
        # 검색어와 비슷한 데이터 가져오기
        cursor.execute(f"SELECT * FROM covid_012 where 국가 like '%{self.search_word}%'"
                            f"and 삭제여부 = '0' order by 국가 and 날짜")
        self.result = cursor.fetchall()

        # 검색결과 없을때
        if self.result==():
            QMessageBox.information(self, '검색', f'{self.search_word}에 대한 검색결과가 없습니다.')
            return
        for i in range(len(self.result)):
            print(self.result[i])
        self.covid_table.setRowCount(len(self.result))
        Row = 0
        # 검색결과 테이블위젯에 넣기
        for k in self.result:
            self.covid_table.setItem(Row, 0, QTableWidgetItem(k[0]))         # 날짜
            self.covid_table.setItem(Row, 1, QTableWidgetItem(k[2]))         # 국가
            self.covid_table.setItem(Row, 2, QTableWidgetItem(str(k[4])))    # 신규 확진자
            self.covid_table.setItem(Row, 3, QTableWidgetItem(str(k[5])))    # 누적 확진자
            self.covid_table.setItem(Row, 4, QTableWidgetItem(str(k[6])))    # 신규 사망자
            self.covid_table.setItem(Row, 5, QTableWidgetItem(str(k[7])))    # 누적 사망자
            Row += 1
        conn.close()
    # 수정 재확인 및 수정불가 체크, 메시지박스
    def check_change(self):
        # 선택된 셀이 없을 경우
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
        # 수정된 값이 없을 경우
        elif self.data[4:-1] == (int(self.new_cases),int(self.cumulative_cases),int(self.new_deaths),int(self.cumulative_deaths)):
            QMessageBox.information(self, '수정', '수정된 값이 없습니다.')
        else:
            ck_chage = QMessageBox.question(self, '수정', '수정 하시겠습니까?', QMessageBox.Yes | QMessageBox.No, )
            if ck_chage == QMessageBox.Yes:
                self.change_data()
            else: return
    # 수정값 데이터 업로드 및 수정완료 메시지 박스
    def change_data(self):
        try:
            self.covid_table.setEditTriggers(QAbstractItemView.AllEditTriggers)    # 테이블 위젯 수정 가능하게 변경

            conn = pymysql.connect(host='10.10.21.101', port=3306, user='test1', password='0000', db='sql_dibidibidib',
                                   charset='utf8')
            cursor = conn.cursor()
            cursor.execute(f"UPDATE covid_012 SET 신규확진자='{self.new_cases}', 누적확진자='{self.cumulative_cases}', 신규사망자='{self.new_deaths}', 누적사망자='{self.cumulative_deaths}'"
                                f"where 날짜='{self.data[0]}' and 국가='{self.data[2]}'")
            conn.commit()
            conn.close()
            QMessageBox.information(self, '수정', '수정되었습니다.')
        except: pass

    # 삭제 재확인 및 삭제불가 메시지박스
    def check_del(self):
        if self.covid_table.currentRow()== -1:
            QMessageBox.information(self, '삭제', '선택된 값이 없습니다.')
            return
        ck_del = QMessageBox.question(self, '삭제', '삭제 하시겠습니까?', QMessageBox.Yes | QMessageBox.No)
        if ck_del == QMessageBox.Yes:
            self.delete_data()
    # 삭제한 데이터 업로드 및 삭제 메시지 박스
    def delete_data(self):
        try:
            self.data = self.result[self.covid_table.currentRow()]              # 테이블 위젯의 result 값을 data에 저장
            conn = pymysql.connect(host='10.10.21.101', port=3306, user='test1', password='0000', db='sql_dibidibidib',
                                   charset='utf8')
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE covid_012 SET 삭제여부= CONCAT ('1')"
                f"where 날짜='{self.data[0]}' and 국가='{self.data[2]}'")
            conn.commit()
            conn.close()
            QMessageBox.information(self, '삭제','삭제되었습니다.')
        except: return


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QtWidgets.QStackedWidget()

    covid_project = Covid_project()
    widget.addWidget(covid_project)

    widget.setFixedWidth(1500)
    widget.setFixedHeight(850)
    widget.show()
    app.exec_()


