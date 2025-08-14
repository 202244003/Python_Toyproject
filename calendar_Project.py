"""
캘린더 일정 관리 프로젝트

1. 캘린더 기본 기능
    - 오늘 날짜 기준으로 달력 불러오기
    - < >를 통해 월 별 이동
    - 드롭다운 박스로 원하는 달로 이동
2. 일정 관리 기능
    - 날짜 클릭을 통한 일정 추가
    - 일정 내용 및 색상 지정
    - 여러 개의 일정 추가 가능
    - 추가한 일정 수정 및 삭제 가능
    - 일정 내용 줄이기 (크기 조절)
3. 파일 관리 기능
    - 생성된 일정을 파일로 저장
    - 파일에 저장된 일정 불러오기

"""

import tkinter as tk
from ast import literal_eval
from tkinter import ttk, simpledialog, colorchooser, messagebox
import calendar
from datetime import datetime

def format_date(date_key):    # 날짜 형식 변경
    year, month, day = date_key.split('-')
    return f"{year}년 {int(month)}월 {int(day)}일"

def truncate_text(text, max_length):      # 최대 글자를 넘어가면 "..."
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

class CalendarApp:
    def __init__(self, root):
        self.root = root                    # root = 부모 창
        self.root.title("캘린더 일정 관리")

        now = datetime.now()                # 현재 날짜로 초기화
        self.year = now.year
        self.month = now.month

        self.schedule_data = {}             # 일정 저장할 딕셔너리 {"YYYY-MM-DD" : {"content" : 0000, "color" : 0000}}

        self.cell_width = 120               # 기본 크기 지정
        self.cell_height = 100
        self.max_event_display = 4          # 일정 최대 보이는 개수

        self.create_widgets()               # 위젯 생성
        self.draw_calendar()                # 달력 생성

    def create_widgets(self):               # 페이지 생성
        # 상단 헤더 프레임
        header_frame = tk.Frame(self.root)
        header_frame.pack(pady=10)

        # 이전 달
        tk.Button(header_frame, text="<", command=self.prev_month,
                  font=("맑은고딕", 12)).pack(side="left", padx=5)
        # 년월 표시
        self.header_label = tk.Label(header_frame, text="", font=("맑은고딕", 16, "bold"))
        self.header_label.pack(side="left", padx=15)
        # 다음 달
        tk.Button(header_frame, text=">", command=self.next_month,
                  font=("맑은고딕", 12)).pack(side="left", padx=5)

        # 년도 드롭다운
        self.year_var = tk.IntVar(value=self.year)
        year_combo = ttk.Combobox(header_frame, values=list(range(1980, 2030)),
                                  width=6, textvariable=self.year_var, state="readonly")
        year_combo.pack(side="left", padx=(20, 5))
        year_combo.bind("<<ComboboxSelected>>", self.on_dropdown_change)

        # 월 드롭다운
        self.month_var = tk.IntVar(value=self.month)
        month_combo = ttk.Combobox(header_frame, values=list(range(1, 13)),
                                  width=4, textvariable=self.month_var, state="readonly")
        month_combo.pack(side="left", padx=(20, 5))
        month_combo.bind("<<ComboboxSelected>>", self.on_dropdown_change)

        # 버튼 프레임
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        #저장
        save_button = ttk.Button(button_frame, text="저장", command=self.save_schedule_to_file)
        save_button.pack(side="left", padx=5)
        #불러오기
        load_button = ttk.Button(button_frame, text="불러오기", command=self.load_schedule_from_file)
        load_button.pack(side="left", padx=5)

        # 달력 프레임
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(padx=10, pady=10)

    def prev_month(self):       # 이전 달
        if self.month == 1:     # 1월이면
            self.month = 12     # 12월로 바꾸기
            self.year -= 1      # 전 년도로
        else:
            self.month -= 1     # 이전 달로
        self.draw_calendar()    # 달력 다시 그리기

    def next_month(self):       # 다음 달
        if self.month == 12:    # 12월이면
            self.month = 1      # 1월로 바꾸기
            self.year += 1      # 다음 년도로
        else:
            self.month += 1     # 다음 달로
        self.draw_calendar()    # 달력 다시 그리기

    def on_dropdown_change(self, event=None):   # 드롭다운 변경시 함수
        self.year = self.year_var.get()     # 선택된 년도로 변경
        self.month = self.month_var.get()   # 선택된 달로 변경
        self.draw_calendar()

    def draw_calendar(self):        # 달력 그리기
        self.header_label.config(text=f"{self.year}년 {self.month}월")
        self.year_var.set(self.year)        # 드롭다운 기본 설정 (년)
        self.month_var.set(self.month)      # 드롭다운 기본 설정 (월)

        for widget in self.calendar_frame.winfo_children():     # 기존 달력 위젯 지우기
            widget.destroy()

        weekdays = ["일", '월', '화', '수', '목', '금', '토']
        for col, day_name in enumerate(weekdays):   # 요일 Header
            text_color = "red" if col == 0 or col == 6 else "black"     # 주말은 빨간색 (라벨)
            day_label = tk.Label(self.calendar_frame, text=day_name,
                                 font=("Arial", 12, "bold"), fg=text_color,
                                 width=15, height=2, bg="#e8e8e8")
            day_label.grid(row=0, column=col, sticky="nsew")

        calendar.setfirstweekday(calendar.SUNDAY)                       # 일요일부터 시작
        cal = calendar.Calendar(firstweekday=6)                         # 토요일 기준 (monthdayscalendar 출력과 일치)
        month_days = cal.monthdayscalendar(self.year, self.month)       # 2차원 배열로 반환

        for week_num, week in enumerate(month_days):                    # 주 인덱스
            for day_col, day in enumerate(week):
                self.create_date_cell(week_num + 1, day_col, day)       # 0행은 헤더, 1행부터 배치

    def create_date_cell(self, row, col, day):          # 날짜 셀 프레임
        cell_frame = tk.Frame(self.calendar_frame, bd=1, relief="solid",
                              width=self.cell_width, height=self.cell_height)
        cell_frame.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
        cell_frame.grid_propagate(False)    # 내부 위젯 크기에 따라 셀 크기가 자동 조절되지 않도록 차단함

        if day == 0:        # 빈 날짜 셀
            return

        date_key = f"{self.year}-{self.month}-{day:02d}" # 날짜 조회에 사용할 key

        text_color = "red" if col == 0 or col == 6 else "black"         # 주말은 빨간색 (날짜)
        day_label = tk.Label(cell_frame, text=str(day), font=("Arial", 11, "bold"), # 날짜 박스
                             fg=text_color, anchor="nw")
        day_label.pack(anchor="nw", padx=3, pady=2)

        events_area = tk.Frame(cell_frame)                              # 일정 프레임
        events_area.pack(fill="both", expand=True, padx=3, pady=(0, 3))

        if date_key in self.schedule_data:                              # schedule_data에 일정이 있으면
            events_list = self.schedule_data[date_key]                  # 해당 날짜를 key로 탐색

            for i, event in enumerate(events_list[:self.max_event_display]):    # 최대 일정 수만큼 표시
                display_text = truncate_text(event["content"], 12)         # 내용이 길면 자르기
                event_box = tk.Label(events_area, text=display_text, bg=event["color"],
                                     fg="white", font=("Arial", 8), padx=2, pady=1,
                                     width=14, anchor='w')
                event_box.pack(fill="x", pady=1)
                event_box.bind("<Button-1>",
                               lambda e, d=date_key, idx=i: self.ask_edit_or_delete(d, idx))    # 추가된 일정 클릭 시 수정 or 삭제

            remaining_count = len(events_list) - self.max_event_display         # 그 날짜에 일정이 너무 많으면 "...n개 더"
            if remaining_count > 0:
                more_label = tk.Label(events_area, text=f"...+{remaining_count}개 더",
                                        fg = "gray", font = ("Arial", 8))
                more_label.pack(pady=1)

        else:# 일정이 없을 때 공간 확보
            placeholder = tk.Label(events_area, text="", font=("Arial", 8), height=6)
            placeholder.pack()

        for widget in [cell_frame, day_label, events_area]:     # 날짜 영역 클릭하면 일정 추가
            widget.bind("<Button-1>", lambda e, d=date_key: self.add_event(d))

    def add_event(self, date_key):      # 선택한 날짜에 일정 추가
        display_date = format_date(date_key)
        event_text = simpledialog.askstring("일정 추가", f"{display_date}에 추가할 일정을 입력하세요.: ")
        if not event_text:      # 아무것도 입력하지 않으면
            return
        color_result = colorchooser.askcolor(title="색상 선택")
        event_color = color_result[1] if color_result[1] else "#4CAF50"     # 사용자가 선택한 색 저장 (없으면 기본값)

        if date_key not in self.schedule_data:          # 해당 날짜에 저장된 일정이 없으면 새로 생성
            self.schedule_data[date_key] = []           # 초기화

        self.schedule_data[date_key].append({          # 해당 날짜에 딕셔너리 추가
            "content" : event_text,
            "color" : event_color
        })

        self.draw_calendar()                            # 달력 다시 그리기 (일정 추가)

    def ask_edit_or_delete(self, date_key, event_index):    # 일정 수정/삭제
        answer = messagebox.askquestion("일정 수정/삭제", "수정하시겠습니까? 삭제하려면 '아니오'를 눌러주세요.", icon='question')
        if answer == 'yes':
            self.edit_event(date_key, event_index)      # 수정
        else:
            self.delete_event(date_key, event_index)    # 삭제

    def edit_event(self, date_key, event_index):            # 일정 수정
        if date_key not in self.schedule_data or event_index >= len(self.schedule_data[date_key]): # 해당 날짜에 일정이 없으면 종료
            return
        old_event = self.schedule_data[date_key][event_index]   # 기존 일정
        old_text = old_event["content"]
        old_color = old_event["color"]
        display_date = format_date(date_key)
        new_text = simpledialog.askstring("일정 수정", f"{display_date} 일정을 수정하세요:", initialvalue=old_text)     # 새로운 정보 입력받기
        if new_text is None:    # 입력한 내용이 없으면 종료
            return
        color_result = colorchooser.askcolor(title="일정 색상 선택", color=old_color)     # 색상 재선택
        new_color = color_result[1] if color_result[1] else old_color   # 선택 없으면 원래 색상
        self.schedule_data[date_key][event_index] = {"content": new_text, "color": new_color}   # 딕셔너리 수정
        self.draw_calendar()    # 달력 다시 그리기

    def delete_event(self, date_key, event_index):      # 삭제
        if date_key in self.schedule_data and event_index < len(self.schedule_data[date_key]):  # 해당 날짜에 일정이 없으면 종료
            del self.schedule_data[date_key][event_index]   # 해당 날짜의 일정 삭제
            if not self.schedule_data[date_key]:            # 날짜의 일정이 없으면
                del self.schedule_data[date_key]            # 날짜도 삭제
            self.draw_calendar()    # 달력 다시 그리기

    def save_schedule_to_file(self, filename="./calendar.txt"):   # 파일 저장
        try:
            with open(filename, "w", encoding="utf-8") as f:
                for date, events in self.schedule_data.items(): # 저장된 데이터
                    for event in events:    # 날짜 key 안의 내용 ({"content":00, "color":00})
                        line = f'{{"{date}": {{"content": "{event["content"]}", "color": "{event["color"]}"}}}}\n'
                        f.write(line)   # 파일에 저장
            messagebox.showinfo("저장 완료", "파일이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("저장 실패", f"오류가 발생했습니다:\n{e}")

    def load_schedule_from_file(self, filename="./calendar.txt"): # 파일 불러오기
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:              # 한 줄 씩
                    line = line.strip()
                    if not line:
                        continue
                    data = literal_eval(line)       # 문자열을 딕셔너리로 처리
                    for date_key, event in data.items():
                        if date_key not in self.schedule_data:  # 해당 날짜에 일정이 없었으면
                            self.schedule_data[date_key] = []   # 새로 리스트 생성
                        self.schedule_data[date_key].append(event)  # 해당 날짜에 일정 추가
            self.draw_calendar()
            messagebox.showinfo("불러오기 완료", "일정을 불러왔습니다.")
        except Exception as e:
            messagebox.showerror("불러오기 실패", f"오류가 발생했습니다:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = CalendarApp(root)
    root.mainloop()
