# Python Toy Project - LGU+ 8기 윤예빈

## 프로젝트 개요

### 주제

- 캘린더 일정 관리 프로젝트
- 기본 캘린더 기능 + 일정 관리
- 파일에 저장 및 불러오기

### 기능

1. 캘린더 기본 기능
    1. 오늘 날짜 기준으로 달력 불러오기
    2. < >를 통해 월 별 이동
    3. 드롭다운 박스로 원하는 달로 이동
2. 일정 관리 기능
    1. 날짜 클릭을 통한 일정 추가
    2. 일정 내용 및 색상 지정
    3. 여러 개의 일정 추가 가능
    4. 추가한 일정 수정 및 삭제 가능
    5. 일정 내용 줄이기 (크기 조절)
3. 파일 관리 기능
    1. 생성된 일정을 파일로 저장
    2. 파일에 저장된 일정 불러오기

### 주요 코드

- 이전 달 다음 달
    
    ```python
    class CalendarApp:
    		...
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
    
    """
    이전 달 버튼을 누르면 self.month를 -1 한다.
    이때, 1월인 경우에는 self.month를 12로 설정하고 년도를 -1한다.
    다음 달 버튼을 누르면 self.month를 +1 한다.
    이떄, 12월인 경우에는 self.month를 1로 설정하고 년도를 +1한다.
    """        
    ```
    
- 날짜 프레임에 일정 프레임 추가
    
    ```python
    class CalendarApp:
    		...
    		def create_data_cell(self, row, col, day):       
            ...
            if date_key in self.schedule_data:                              # schedule_data에 일정이 있으면
                events_list = self.schedule_data[date_key]                  # 해당 날짜를 key로 탐색
    
                for i, event in enumerate(events_list[:self.max_event_display]):    # 최대 일정 수만큼 표시
                    display_text = self.truncate_text(event["content"], 12)         # 내용이 길면 자르기
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
         ...
    
    """
    schedule_data에 해당 날짜가 key인 값이 없다면 새로 생성하고, 있다면 정보를 불러온다.
    일정 내용이 12자가 넘는 경우 ...를 출력하여 생략한다.
    최대 일정 수 는 4개로, 이 이상은 ...+n개더 라는 메시지와 함께 생략된다.
     
    """
    ```
    
- 일정 추가
    
    ```python
    class CalendarApp:
    		...
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
        ...
        
    """
    선택한 날짜가 key인 일정을 schecule_data에서 찾는다.
    없으면 그 날짜를 key로 하는 리스트를 생성한다.
    그리고 그 리스트에 사용자가 입력한 일정의 content와 color 값을 append 한다.
    이후 추가된 일정을 적용하기 위해 달력을 다시 그린다.
    """
    ```
    
- 일정 수정 / 삭제
    
    ```python
    class CalendarApp:
    		...
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
        ...
    
    """
    수정
    해당 날짜에 일정이 없거나 인덱스가 비어있으면 종료.
    선택된 기존 일정의 content와 color를 불러온다.
    기본값을 기존 content와 color로 두고 사용자에게 새로운 정보를 입력 받는다.
    입력이 없으면 종료하거나 기본 값으로 설정한다.
    새로운 정보로 일정 딕셔너리를 수정한다.
    수정된 내용을 적용하기 위해 달력을 다시 그린다.
    
    삭제
    해당 날짜에 일정이 없거나 인덱스가 비어있으면 종료.
    해당 일정을 일정 딕셔너리에서 삭제.
    해당 날짜의 일정이 없으면 날짜가 key인 딕셔너리 삭제.
    """
    ```
    
- 파일 저장
    
    ```python
    class CalendarApp:
    		...
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
    
    """
    schedule_data에 저장된 데이터를 파일에 저장한다.
    for 문으로 schedule_data안의 내용들을 뽑아서 {날짜: {"content":내용, "color":색상}} 형태로 한 줄씩 저장한다.
    실패시 오류를 출력한다.
    """
    ```
    
- 파일 불러오기
    
    ```python
    class CalendarApp:
    		...
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
    
    """
    calendar.txt에 저장된 내용을 불러와서 schedule_data에 저장한다.
    {날짜: {"content":내용, "color":색상}} 형태의 문자열로 저장된 데이터를 literal_eval를 사용해 딕셔너리로 변환한다.
    해당 날짜가 key인 리스트가 없다면 새로 생성한다.
    불러온 내용을 schedule_data에 저장한다.
    새로 저장한 내용을 적용하기 위해 달력을 새로 그린다.
    실패시 오류를 출력한다.
    """
    ```