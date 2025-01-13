import math
import re
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import datetime

import externalFunction as exF


class main:
    def __init__(self, root):
        self.root = root
        self.root.title("Delte Old Neighbor")

        self.CDM, self.options, self.chrome_options = exF.chromeDriverSetting()
        self.driver = None

        self.id_btn = None
        self.id_label = None
        self.file_name = tk.StringVar()

        self.common_params = {
            'locale': 'ko_KR', 'width': 12, 'borderwidth': 0, 'state': 'readonly', 'date_pattern': 'yy.mm.dd.'
            , 'maxdate': datetime.now().date()
            , 'showweeknumbers': False
            , 'background': 'white', 'foreground': 'black'
            , 'headersbackground': 'white', 'headersforeground': 'black'
            , 'normalbackground': 'white', 'normalforeground': 'black'
            , 'weekendbackground': 'white', 'weekendforeground': 'black'
            , 'othermonthbackground': 'white', 'othermonthforeground': 'lightgray'
            , 'othermonthwebackground': 'white', 'othermonthweforeground': 'lightgray'
            , 'selectbackground': 'lightgray', 'selectforeground': 'black'
        }

        self.sent_app_state = None
        self.sent_app = None
        self.s_cal = None

        self.neighbor_state = None
        self.neighbor = None
        self.n_cal = None

        self.neighbor_together_state = None
        self.neighbor_together = None
        self.nt_cal = None

        self.id_info_text = None
        self.start_btn = None
        self.log_text = None

        self.macro_thread = None
        self.is_running = True

        self.id_list = {}

        self.create_gui()

    def create_gui(self):
        top_frame = tk.Frame(self.root, padx=5, pady=5)
        top_frame.pack(side="top", fill="both", expand=True)

        login_data_frame = tk.Frame(top_frame, padx=5, pady=5)
        login_data_frame.pack(fill='x')
        self.id_btn = tk.Button(login_data_frame, text="아이디 불러오기", command=self.select_txt)
        self.id_btn.pack(side="left")
        self.id_label = tk.Label(login_data_frame, textvariable=self.file_name)
        self.id_label.pack(side="left", expand=True)

        check_frame = tk.Frame(top_frame, padx=5, pady=5)
        check_frame.pack(fill='x', side="left")
        self.sent_app_state = tk.BooleanVar()
        self.sent_app_state.set(False)
        self.sent_app = tk.Checkbutton(check_frame, text="보낸 신청", variable=self.sent_app_state)
        self.sent_app.pack(anchor="w")
        self.s_cal = DateEntry(check_frame, **self.common_params)
        self.s_cal.pack(anchor="w")
        self.neighbor_state = tk.BooleanVar()
        self.neighbor_state.set(False)
        self.neighbor = tk.Checkbutton(check_frame, text="이웃", variable=self.neighbor_state)
        self.neighbor.pack(anchor="w")
        self.n_cal = DateEntry(check_frame, **self.common_params)
        self.n_cal.pack(anchor="w")
        self.neighbor_together_state = tk.BooleanVar()
        self.neighbor_together_state.set(False)
        self.neighbor_together = tk.Checkbutton(check_frame, text="서로 이웃", variable=self.neighbor_together_state)
        self.neighbor_together.pack(anchor="w")
        self.nt_cal = DateEntry(check_frame, **self.common_params)
        self.nt_cal.pack(anchor="w")

        login_log_frame = tk.Frame(top_frame, padx=5, pady=5)
        login_log_frame.pack()
        self.id_info_text = tk.Text(top_frame, width=65, height=10)
        self.id_info_text.pack()
        self.id_info_text.config(state=tk.DISABLED)

        self.start_btn = tk.Button(self.root, text="시작", command=self.change_flag)
        self.start_btn.pack(fill="x", anchor="s", expand=True)

        bottom_frame = tk.Frame(self.root, padx=5, pady=5)
        bottom_frame.pack(side="bottom", fill="both", expand=True)
        bottom_frame.config(height=100)
        self.log_text = tk.Text(bottom_frame)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.config(state=tk.DISABLED)

    def select_txt(self):
        # 파일 열기
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Txt File", " *.txt")])

            with open(file_path, 'r', encoding='utf-8') as file:
                self.id_list = {}
                self.file_name.set("")
                exF.logDelete(self.id_info_text)
                lines = file.readlines()

                for line in lines:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        parts = cleaned_line.split(",")
                        if not (len(parts) == 2 and all(part.strip() for part in parts)):
                            self.file_name.set("txt 파일의 형식을 확인하세요.")
                            exF.logInsert(self.id_info_text, False, cleaned_line)
                            return
                        else:
                            self.id_list[parts[0]] = parts[1]
                            exF.logInsert(self.id_info_text, False, f'아이디 : {parts[0]} / 비밀번호 : {parts[1]}')

                self.file_name.set(file_path)
        except Exception as e:
            print(e)

    def change_flag(self):
        if not self.file_name.get() or self.file_name.get() == "txt 파일의 형식을 확인하세요.":
            exF.logInsert(self.log_text, False, "txt 파일의 형식을 확인하세요.")
            return
        if not (self.sent_app_state.get() or self.neighbor_state.get() or self.neighbor_together_state.get()):
            exF.logInsert(self.log_text, False, "삭제 옵션을 선택하세요.")
            return

        self.start_btn.config(state="disabled")
        if self.start_btn.cget("text") == "시작":
            self.state_change("disabled")

            self.is_running = True
            self.macro_thread = threading.Thread(target=self.macro_start, daemon=True)
            self.macro_thread.start()
        else:
            self.state_change("normal")

            self.is_running = False
            self.macro_thread = None

    def state_change(self, state):
        self.id_btn.config(state=state)

        self.sent_app.config(state=state)
        self.neighbor.config(state=state)
        self.neighbor_together.config(state=state)

        self.s_cal.config(state=state)
        self.n_cal.config(state=state)
        self.nt_cal.config(state=state)

    def forcedTermination(self):
        if not self.is_running:
            if self.driver:
                self.driver.quit()
                self.driver = None
            exF.logInsert(self.log_text, True, "강제 종료 됐습니다.")
            exF.update_button(self.start_btn, "text", "시작")
            self.state_change("normal")
            return True
        return False

    def macro_start(self):
        exF.logDelete(self.log_text)
        log_text = '[삭제 옵션] '
        if self.sent_app_state.get():
            log_text += f'보낸 신청({self.s_cal.get()})'
        if self.neighbor_state.get():
            if log_text != '[삭제 옵션] ':
                log_text += ', '
            log_text += f'이웃({self.n_cal.get()})'
        if self.neighbor_together_state.get():
            if log_text != '[삭제 옵션] ':
                log_text += ', '
            log_text += f'서로 이웃({self.nt_cal.get()})'
        exF.logInsert(self.log_text, True, log_text)

        if self.forcedTermination():
            return

        self.driver = exF.chromeDriverStart(self.CDM, self.options, self.chrome_options)
        exF.update_button(self.start_btn, "text", "종료")

        log_text = '작업을 시작합니다.'
        exF.logInsert(self.log_text, True, log_text)

        try:
            for id_pw in self.id_list:
                log_text = f'{id_pw} 계정 로그인 시도 중...'
                exF.logInsert(self.log_text, True, log_text)
                if self.forcedTermination():
                    return
                login_chk = exF.naverLogin(self.driver, id_pw, self.id_list[id_pw])
                if not login_chk:
                    log_text = f'{id_pw} 계정 로그인 실패'
                    exF.logInsert(self.log_text, True, log_text)
                    continue

                log_text = f'{id_pw} 계정 로그인 성공'
                exF.logInsert(self.log_text, True, log_text)
                if self.forcedTermination():
                    return

                url = 'https://blog.naver.com/MyBlog.naver'
                self.driver.get(url)

                if self.forcedTermination():
                    return

                cur_url = self.driver.current_url
                blog_id = cur_url.split("/")[-1]
                if self.is_running and self.sent_app_state.get():
                    self.buddyInviteSentManage(blog_id)
                    if self.forcedTermination():
                        return
                if self.is_running and self.neighbor_state.get():
                    self.buddyListManage(blog_id, 0)
                    if self.forcedTermination():
                        return
                if self.is_running and self.neighbor_together_state.get():
                    self.buddyListManage(blog_id, 1)
                    if self.forcedTermination():
                        return
        except Exception as e:
            print(e)
            log_text = f'ERROR 7'
            exF.logInsert(self.log_text, True, log_text)
            if self.forcedTermination():
                return

        self.driver.quit()
        self.state_change("normal")
        self.macro_thread = None

        if self.is_running:
            log_text = '모든 작업을 완료했습니다.'
            exF.logInsert(self.log_text, True, log_text)
        else:
            log_text = '강제 종료 됐습니다.'
            exF.logInsert(self.log_text, True, log_text)

        exF.update_button(self.start_btn, "text", "시작")

    # 보낸 신청
    def buddyInviteSentManage(self, blogId):
        log_text = f'{self.s_cal.get()} 이전 보낸 신청 삭세를 시작합니다.'
        exF.logInsert(self.log_text, True, log_text)
        sent_url = f'https://admin.blog.naver.com/BuddyInviteSentManage.naver?blogId={blogId}'
        self.driver.get(sent_url)
        if not self.is_running:
            return

        # 페이징 찾기
        none_tr = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr/td')
        none_tr_class = none_tr.get_attribute("class")
        if none_tr_class == "none":
            log_text = f'{self.s_cal.get()} 이전 보낸 신청 삭세를 완료했습니다.'
            exF.logInsert(self.log_text, True, log_text)
            return

        a_tags = exF.findEl(self.driver, "xpath", '//*[@id="invite"]/div[4]/a')
        if not a_tags:
            log_text = f'ERROR 1'
            exF.logInsert(self.log_text, True, log_text)
            if self.forcedTermination():
                return

        if a_tags:
            last_a_tag = a_tags[-1]
            match = re.search(r'goPage\((\d+)\)', last_a_tag.get_attribute("href"))

            page_number = match.group(1) if match else None

            for i in range(int(page_number), 0, -1):
                if not self.is_running:
                    return
                try:
                    url = f'https://admin.blog.naver.com/BuddyInviteSentManage.naver?blogId={blogId}&currentPage={i}'
                    self.driver.get(url)
                except Exception as e:
                    print(e)
                    log_text = f'ERROR 2'
                    exF.logInsert(self.log_text, True, log_text)
                    if self.forcedTermination():
                        return
                if not self.is_running:
                    return

                try:
                    tbody_list = exF.elLoChildEl(self.driver, '//*[@id="invite"]/table/tbody')
                    last_index = len(tbody_list)
                    if len(tbody_list) > 1:
                        first_date = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr[1]/td[4]')
                        end_date = exF.elLo(self.driver, "xpath",
                                            f'//*[@id="invite"]/table/tbody/tr[{last_index}]/td[4]')
                    else:
                        first_date = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr/td[4]')
                        end_date = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr/td[4]')

                    date_format = "%y.%m.%d."
                    format_first_date = datetime.strptime(first_date.text, date_format)
                    format_s_cal = datetime.strptime(self.s_cal.get(), date_format)
                    format_end_date = datetime.strptime(end_date.text, date_format)

                    if format_first_date <= format_s_cal:
                        # 전체 선택
                        exF.elementClick(self.driver, "xpath", '//*[@id="invite"]/table/thead/tr/th[1]/input')
                    elif format_s_cal < format_end_date:
                        break
                    else:
                        for j in range(len(tbody_list)):
                            if not self.is_running:
                                return
                            date_url = f'//*[@id="invite"]/table/tbody/tr[{j + 1}]/td[4]'
                            tr_date = exF.elLo(self.driver, "xpath", date_url)
                            format_tr_date = datetime.strptime(tr_date.text, date_format)

                            checkbox_url = f'//*[@id="invite"]/table/tbody/tr[{j + 1}]/td[1]/input'
                            if format_tr_date <= format_s_cal:
                                exF.elementClick(self.driver, "xpath", checkbox_url)
                except Exception as e:
                    print(e)
                    log_text = f'ERROR 3'
                    exF.logInsert(self.log_text, True, log_text)
                    if self.forcedTermination():
                        return

                if not self.is_running:
                    return

                # 내역 삭제
                try:
                    exF.elementClick(self.driver, "xpath", '//*[@id="invite"]/div[2]/div/span/button')
                    while exF.alertChk(self.driver):
                        alert = self.driver.switch_to.alert
                        alert.accept()
                except Exception as e:
                    print(e)
                    log_text = f'ERROR 4'
                    exF.logInsert(self.log_text, True, log_text)
                    if self.forcedTermination():
                        return

                log_text = f'{i} 페이지의 정보를 삭세합니다.'
                exF.logInsert(self.log_text, True, log_text)
        else:
            if not self.is_running:
                return
            try:
                url = f'https://admin.blog.naver.com/BuddyInviteSentManage.naver?blogId={blogId}&currentPage=1'
                self.driver.get(url)
            except Exception as e:
                print(e)
                log_text = f'ERROR 2'
                exF.logInsert(self.log_text, True, log_text)
                if self.forcedTermination():
                    return
            if not self.is_running:
                return

            try:
                tbody_list = exF.elLoChildEl(self.driver, '//*[@id="invite"]/table/tbody')
                last_index = len(tbody_list)
                if last_index > 1:
                    first_date = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr[1]/td[4]')
                    end_date = exF.elLo(self.driver, "xpath", f'//*[@id="invite"]/table/tbody/tr[{last_index}]/td[4]')
                else:
                    first_date = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr/td[4]')
                    if not first_date:
                        log_text = f'{self.s_cal.get()} 이전 보낸 신청 삭세를 완료했습니다.'
                        exF.logInsert(self.log_text, True, log_text)
                        return
                    end_date = exF.elLo(self.driver, "xpath", '//*[@id="invite"]/table/tbody/tr/td[4]')
                date_format = "%y.%m.%d."
                format_first_date = datetime.strptime(first_date.text, date_format)
                format_s_cal = datetime.strptime(self.s_cal.get(), date_format)
                format_end_date = datetime.strptime(end_date.text, date_format)

                if format_first_date <= format_s_cal:
                    # 전체 선택
                    exF.elementClick(self.driver, "xpath", '//*[@id="invite"]/table/thead/tr/th[1]/input')
                elif format_s_cal < format_end_date:
                    pass
                else:
                    for i in range(last_index):
                        if not self.is_running:
                            return
                        date_url = f'//*[@id="invite"]/table/tbody/tr[{i + 1}]/td[4]'
                        tr_date = exF.elLo(self.driver, "xpath", date_url)
                        format_tr_date = datetime.strptime(tr_date.text, date_format)

                        checkbox_url = f'//*[@id="invite"]/table/tbody/tr[{i + 1}]/td[1]/input'
                        if format_tr_date <= format_s_cal:
                            exF.elementClick(self.driver, "xpath", checkbox_url)
            except Exception as e:
                print(e)
                log_text = f'ERROR 3'
                exF.logInsert(self.log_text, True, log_text)
                if self.forcedTermination():
                    return

            if not self.is_running:
                return

            # 내역 삭제
            try:
                exF.elementClick(self.driver, "xpath", '//*[@id="invite"]/div[2]/div/span/button')
                while exF.alertChk(self.driver):
                    alert = self.driver.switch_to.alert
                    alert.accept()
            except Exception as e:
                print(e)
                log_text = f'ERROR 4'
                exF.logInsert(self.log_text, True, log_text)
                if self.forcedTermination():
                    return
            log_text = f'1 페이지의 정보를 삭세합니다.'
            exF.logInsert(self.log_text, True, log_text)
        log_text = f'{self.s_cal.get()} 이전 보낸 신청 삭세를 완료했습니다.'
        exF.logInsert(self.log_text, True, log_text)

    # 이웃 / 서로 이웃
    def buddyListManage(self, blogId, relation):
        log_text = f'{self.n_cal.get()} 이전 이웃 삭세를 시작합니다.'
        if relation == 1:
            log_text = f'{self.nt_cal.get()} 이전 서로 이웃 삭세를 시작합니다.'
        exF.logInsert(self.log_text, True, log_text)
        try:
            admin_url = f'https://admin.blog.naver.com/{blogId}'
            self.driver.get(admin_url)
        except Exception as e:
            print(e)
            log_text = f'ERROR 5'
            exF.logInsert(self.log_text, True, log_text)
            if self.forcedTermination():
                return
        if not self.is_running:
            return

        try:
            exF.elementClick(self.driver, "css", '#buddylist_config_anchor')
            script = f"adminMain.GotoPage('https://admin.blog.naver.com/BuddyListManage.naver?blogId={blogId}&relation={relation}&currentPage=0&searchText=&orderType=adddate', false);"
            self.driver.execute_script(script)
        except Exception as e:
            print(e)
            log_text = f'ERROR 6'
            exF.logInsert(self.log_text, True, log_text)
            if self.forcedTermination():
                return
        if not self.is_running:
            return

        try:
            # 찾은 프레임으로 전환
            frame = exF.findEl(self.driver, "id", "papermain")
            self.driver.switch_to.frame(frame)
            neighbor_tot = int(
                exF.elLo(self.driver, "xpath", '//*[@id="buddyListManageForm"]/div[1]/div[2]/span/strong').text)
            last_pegging = math.ceil(neighbor_tot / 50)
            # 기존 프레임으로 전환
            self.driver.switch_to.default_content()

            for i in range(last_pegging, 0, -1):
                if not self.is_running:
                    return
                script = f"adminMain.GotoPage('https://admin.blog.naver.com/BuddyListManage.naver?blogId={blogId}&relation={relation}&currentPage={i}&searchText=&orderType=adddate', false);"
                self.driver.execute_script(script)
                frame = exF.findEl(self.driver, "id", "papermain")
                self.driver.switch_to.frame(frame)
                if not self.is_running:
                    return

                tbody_list = exF.elLoChildEl(self.driver, '//*[@id="buddyListManageForm"]/table/tbody')
                last_index = len(tbody_list)
                none_tr = exF.elLo(self.driver, "xpath", '//*[@id="buddyListManageForm"]/table/tbody/tr')
                none_tr_class = none_tr.get_attribute("class")
                if none_tr_class == "none":
                    self.driver.switch_to.default_content()
                    continue
                if len(tbody_list) > 1:
                    first_date = exF.elLo(self.driver, "xpath",
                                          '//*[@id="buddyListManageForm"]/table/tbody/tr[1]/td[7]')
                    end_date = exF.elLo(self.driver, "xpath",
                                        f'//*[@id="buddyListManageForm"]/table/tbody/tr[{last_index}]/td[7]')
                else:
                    first_date = exF.elLo(self.driver, "xpath",
                                          '//*[@id="buddyListManageForm"]/table/tbody/tr[1]/td[7]')
                    end_date = exF.elLo(self.driver, "xpath", '//*[@id="buddyListManageForm"]/table/tbody/tr[1]/td[7]')

                date_format = "%y.%m.%d."
                format_first_date = datetime.strptime(first_date.text, date_format)
                format_s_cal = datetime.strptime(self.n_cal.get(), date_format)
                if relation == 1:
                    format_s_cal = datetime.strptime(self.nt_cal.get(), date_format)
                format_end_date = datetime.strptime(end_date.text, date_format)
                if format_first_date <= format_s_cal:
                    # 전체 선택
                    exF.elementClick(self.driver, "xpath", '//*[@id="buddyListManageForm"]/table/thead/tr/th[1]/input')
                elif format_s_cal < format_end_date:
                    break
                else:
                    for j in range(len(tbody_list)):
                        if not self.is_running:
                            return
                        date_url = f'//*[@id="buddyListManageForm"]/table/tbody/tr[{j + 1}]/td[7]'
                        tr_date = exF.elLo(self.driver, "xpath", date_url)
                        format_tr_date = datetime.strptime(tr_date.text, date_format)

                        checkbox_url = f'//*[@id="buddyListManageForm"]/table/tbody/tr[{j + 1}]/td[1]/input'
                        if format_tr_date <= format_s_cal:
                            exF.elementClick(self.driver, "xpath", checkbox_url)

                if not self.is_running:
                    return

                # 내역 삭제
                exF.elementClick(self.driver, "xpath", '//*[@id="buddyListManageForm"]/div[1]/div[1]/span[3]/button')
                exF.elementClick(self.driver, "xpath", '//*[@id="tpl_layer_del"]/div/div/fieldset/div/input')
                self.driver.switch_to.default_content()
                log_text = f'{i} 페이지의 정보를 삭세합니다.'
                exF.logInsert(self.log_text, True, log_text)
        except Exception as e:
            print(e)
            log_text = f'ERROR 7'
            exF.logInsert(self.log_text, True, log_text)
            if self.forcedTermination():
                return

        log_text = f'{self.n_cal.get()} 이전 이웃 삭세를 완료했습니다.'
        if relation == 1:
            log_text = f'{self.nt_cal.get()} 이전 서로 이웃 삭세를 완료했습니다.'
        exF.logInsert(self.log_text, True, log_text)


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.geometry("512x512")
        app = main(root)
        root.mainloop()
    except Exception as e:
        print(e)
