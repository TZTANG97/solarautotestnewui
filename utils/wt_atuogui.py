import pyautogui, pyperclip
import win32gui
import win32con
import time

from SCPITestWave import setting_icon, messure_icon, messure_status,\
    setting_status, config_dict, heading_handle, param_dict

def get_enumwindows():
    hwnd_list = {}
    def foo(hwnd, result):
        if win32gui.IsWindow(hwnd) and \
            win32gui.IsWindowEnabled(hwnd) and \
                win32gui.IsWindowVisible(hwnd):
                hwnd_list.update({hwnd: win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(foo, 0)
    return hwnd_list

def auto_config():
    # global cells_crood
    global setting_icon, messure_icon, messure_status, setting_status, heading_handle, param_dict
    # cells_crood = cell_crood
    if 'WTViewerEfree' in heading_handle.values():
        headle_now_list = {}
        h = list(heading_handle.keys())[list(heading_handle.values()).index('WTViewerEfree')]
        win32gui.ShowWindow(h, win32con.SW_SHOWMAXIMIZED)
        win32gui.SetForegroundWindow(h)
        left_wtv, top_wtv, right_wtv, bottom_wtv = win32gui.GetWindowRect(h)
        print(left_wtv, top_wtv, right_wtv, bottom_wtv)
        # setting_icon = (left_wtv + 8 + 43 ,top_wtv + 8 + 7 + 23 + 81 + 27)
        # messure_icon = (left_wtv + 8 + 43 ,top_wtv + 8 + 7 + 23 + 81 + 81 + 27)
        setting_icon = (left_wtv + 51 ,top_wtv + 146)
        messure_icon = (left_wtv + 51 ,top_wtv + 227)

        win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), param_dict)

        if '开始在线连接' in param_dict.values():
            messure_handle_dict = {}
            key_child_start = list(param_dict.keys())[list(param_dict.values()).index('开始在线连接')]
            left, top, right, bottom = win32gui.GetWindowRect(key_child_start) 
            pyautogui.moveTo(left + (right - left) / 2, top + (bottom - top) / 2, duration=1)
            pyautogui.click()
            # 判断程序连接状态
            loop = True
            param_list1 = {}
            while loop:
                win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), param_list1)
                if param_list1[key_child_start] != '开始在线连接':
                    loop = False
            pyautogui.moveTo(setting_icon[0], setting_icon[1], duration=0.5)
            pyautogui.doubleClick()
            time.sleep(2)
            setting_set(h)
            pyautogui.moveTo(messure_icon[0], messure_icon[1], duration=0.5)
            pyautogui.doubleClick()
            time.sleep(2)
            win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), messure_handle_dict)
            messure_handle_now = list(messure_handle_dict.keys())[list(messure_handle_dict.values()).index('数值')]
            messured_set(messure_handle_now)
            # win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), param_list1)           
        elif '停止在线连接' in param_dict.values():
            messure_handle_dict = {}
            pyautogui.moveTo(setting_icon[0], setting_icon[1], duration=0.5)
            pyautogui.doubleClick()
            time.sleep(2)
            setting_set(h)
            pyautogui.doubleClick(messure_icon[0], messure_icon[1], duration=0.5) 
            pyautogui.click()
            time.sleep(2)
            win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), messure_handle_dict)
            messure_handle_now = list(messure_handle_dict.keys())[list(messure_handle_dict.values()).index('数值')]
            messured_set(messure_handle_now)
        elif "数值列表" not in param_dict.values() and "数值" not in param_dict.values():
            messure_handle_dict = {}
            if setting_status == '':
                key_child_setting = list(param_dict.keys())[list(param_dict.values()).index('接线方式')]
                setting_set(h)
            pyautogui.moveTo(messure_icon[0], messure_icon[1], duration=0.5)
            pyautogui.doubleClick()
            pyautogui.sleep(2)
            win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), messure_handle_dict)
            key_child_messure = list(messure_handle_dict.keys())[list(messure_handle_dict.values()).index('数值')]
            left, top, right, bottom = win32gui.GetWindowRect(key_child_messure)
            messured_set(key_child_messure)
        elif "数值列表" in param_dict.values() and "数值" in param_dict.values():
            if setting_status == '':
                messure_handle_dict = {}
                pyautogui.moveTo(setting_icon[0], setting_icon[1], duration=0.5)
                pyautogui.doubleClick()
                pyautogui.sleep(2)
                setting_set(h)
                pyautogui.moveTo(messure_icon[0], messure_icon[1], duration=0.5)
                pyautogui.doubleClick()
                pyautogui.sleep(2)
                win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), messure_handle_dict)
                messure_handle_now = list(messure_handle_dict.keys())[list(messure_handle_dict.values()).index('数值')]
            else:
                messure_handle_now = list(param_dict.keys())[list(param_dict.values()).index('数值')]
            messured_set(messure_handle_now)

def setting_set(h):
    global setting_icon, messure_icon, messure_status, setting_status, config_dict

    connect_mode = []
    parm_dict_set = {}
    for i in list(config_dict.values())[1:8]:
        connect_mode.append(i)
    win32gui.EnumChildWindows(h, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), parm_dict_set)
    # for i in range(2):
    step = 14
    if "接线方式" in parm_dict_set.values() and setting_status != '1':
        step = 14
        key_child_setting = list(parm_dict_set.keys())[list(parm_dict_set.values()).index('接线方式')]
        left, top, right, bottom = win32gui.GetWindowRect(key_child_setting)
        # local_per = [(left + 81 + 35, top + 94 + 10), (left + 160 + 45, top + 94 + 10), 
        #     (left + 81 + 35, top + 120 + 10), (left + 160 + 45, top + 120 + 10), 
        #     (left + 160 + 35, top + 146 + 10), (left + 160 + 36, top + 172 + 10)]
        local_per = [(left + 116, top + 104), (left + 205, top + 104), 
            (left + 116, top + 130), (left + 205, top + 130), 
            (left + 195, top + 156), (left + 196, top + 182)]
        pyautogui.moveTo( left + (right - left) / 2, top + (bottom - top) / 2, duration=0.5)
        pyautogui.click()
        
        time.sleep(1)
        for j in range(len(connect_mode) - 1):
            param_warn_info_win_dict = {}
            if connect_mode[j] != "":
                handle_now_dict = {}
                pyautogui.moveTo(local_per[j][0], local_per[j][1], duration=0.5)
                pyautogui.click()
                
                chose_step = (int(connect_mode[j]) + 1) * step
                pyautogui.moveTo(local_per[j][0], local_per[j][1] + chose_step, duration=0.5)
                pyautogui.click()
                handle_now_dict = get_enumwindows()
                param_warn_handle = list(handle_now_dict.keys())[list(handle_now_dict.values()).index('WTViewerEfree')]
                win32gui.EnumChildWindows(param_warn_handle, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), param_warn_info_win_dict)
                if '确定' in param_warn_info_win_dict.values() and '不能指定接线的模块。' in param_warn_info_win_dict.values():
                    handle_sure = list(param_warn_info_win_dict.keys())[list(param_warn_info_win_dict.values()).index('确定')]
                    left_warn, top_warn, right_warn, bottom_warn = win32gui.GetWindowRect(handle_sure)
                    pyautogui.moveTo(left_warn + (right_warn - left_warn) / 2, top_warn + (bottom_warn - top_warn) / 2, duration=0.5)
                    pyautogui.click()
                else:
                    pyautogui.sleep(1)
            if j == len(connect_mode) - 2:
                pyautogui.moveTo( left + (right - left) / 2, top + (bottom - top) / 2, duration=0.5)
                pyautogui.click()
    if "更新率" in parm_dict_set.values() and setting_status != '1':
        step = 13
        key_child_setting = list(parm_dict_set.keys())[list(parm_dict_set.values()).index('接线方式')]
        left, top, right, bottom = win32gui.GetWindowRect(key_child_setting)
        # left1, top1, = left + 142, top + 150 + 14
        left1, top1, = left + 142, top + 164
        local_per = (left1, top1 + 31)
        pyautogui.moveTo(left1, top1, duration=0.5)
        pyautogui.click()
        time.sleep(0.2)
        param_warn_info_win_dict = {}
        handle_now_dict = {}
        if connect_mode[-1] != "":
            pyautogui.moveTo(local_per[0], local_per[1], duration=0.5)
            pyautogui.click()
            time.sleep(0.2)
            chose_step = (int(connect_mode[-1]) + 1) * step
            pyautogui.moveTo(local_per[0], local_per[1] + chose_step, duration=0.5)
            pyautogui.click()
            pyautogui.sleep(3)
            handle_now_dict = get_enumwindows()
            param_warn_handle = list(handle_now_dict.keys())[list(handle_now_dict.values()).index('WTViewerEfree')]
            win32gui.EnumChildWindows(param_warn_handle, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), param_warn_info_win_dict)
            if '确定' in param_warn_info_win_dict.values() and '不能指定接线的模块。' in param_warn_info_win_dict.values():
                handle_sure = list(param_warn_info_win_dict.keys())[list(param_warn_info_win_dict.values()).index('确认')]
                left_warn, top_warn, right_warn, bottom_warn = win32gui.GetWindowRect(handle_sure)
                pyautogui.moveTo(left_warn + (right_warn - left_warn) / 2, top_warn + (bottom_warn - top_warn) / 2, duration=0.5)
                pyautogui.click()
            pyautogui.moveTo(left1, top1, duration=0.5)
            pyautogui.click()
    setting_status = '1'

def messured_set(messure_handle):
    global setting_icon, messure_icon, messure_status, setting_status, messsure_deatil_cofig, messure_project_cofig
    global cells_coord, test_time_list, save_file_name, save_file_name, config_dict, check_project_status, start_and_stop_rows

    handle_now_dict = {}
    parm_dict_set = {}
    left, top, right, bottom = win32gui.GetWindowRect(messure_handle)
    print(left, top, right, bottom)
    pyautogui.moveTo(left + (right - left) / 2, top + (bottom - top) / 2, duration=0.5)
    pyautogui.rightClick()
    handle_now_dict = get_enumwindows()
    if "数值详细设置" in handle_now_dict.values():
        deatil_messure_set_handle = list(handle_now_dict.keys())[list(handle_now_dict.values()).index('数值详细设置')]
        win32gui.ShowWindow(deatil_messure_set_handle, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(deatil_messure_set_handle)
        left, top, right, bottom = win32gui.GetWindowRect(deatil_messure_set_handle)
        t1 = (left + 40, top + 43)
        t2 = (left + 100, top + 43)

        connect_messure_mode = []
        for i in list(config_dict.values())[8:]:
            connect_messure_mode.append(i)
        # 数值详细设置界面，各数值设置以及勾选
        if messsure_deatil_cofig == '':
            config_1 = connect_messure_mode[:6]
            pyautogui.moveTo(t1[0], t1[1], duration=0.5)
            pyautogui.click()
            for i in range(len(config_1)):
                if config_1[i] != '':
                    if i == 0:
                        pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top, duration=0.5)
                        pyautogui.click()
                        if int(config_1[i]) == 0:
                            pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top + 18, duration=0.5)
                            pyautogui.click()
                        else:
                            pyautogui.moveTo(
                                cells_coord[1][i][0] + left,
                                cells_coord[1][i][1] + top + 20 + int(config_1[i]) * 11, duration=0.5)
                            pyautogui.click()
                    if i == 1:
                        pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top, duration=0.5)
                        pyautogui.click()
                        if int(config_1[i]) == 0:
                            pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top + 20, duration=0.5)
                            pyautogui.click()
                        else:
                            pyautogui.moveTo(
                                cells_coord[1][i][0] + left,
                                cells_coord[1][i][1] + top + 20 + int(config_1[i]) * 11, duration=0.5)
                            pyautogui.click()
                    if i == 2:
                        if int(config_1[i-1]) == '0' or int(config_1[i-1]) == '2':
                            continue
                        else:
                            test_time_list = [int(value) for value in config_1[i].split(':')]
                            for j in range(len(test_time_list)):
                                if test_time_list[j] == 0:
                                    continue
                                else:
                                    pyautogui.moveTo(cells_coord[1][i][j][0] + left, cells_coord[1][i][j][1] + top, duration=0.5)
                                    pyautogui.doubleClick()
                                    pyautogui.typewrite(str(test_time_list[j]))
                                    pyautogui.sleep(0.2)
                    if i == 3:
                        file_locl = config_1[i]
                        pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top, duration=0.5)
                        pyautogui.click()
                        pyautogui.hotkey('ctrl', 'a', interval=0.5)
                        pyperclip.copy(rf'{file_locl}')
                        pyautogui.hotkey('ctrl', 'V', interval=0.5)
                    if i == 4 and auto_save_file == '':
                        pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top, duration=0.5)
                        pyautogui.click()
                        auto_save_file = '0'
                    if i == 5 and auto_save_file == '0':
                        file_name_list = [value for value in config_1[i].split(',')]
                        pyautogui.moveTo(cells_coord[1][i][0] + left, cells_coord[1][i][1] + top, duration=0.5)
                        pyautogui.click()
                        pyautogui.hotkey('ctrl', 'a', interval=0.2)
                        pyperclip.copy(f'{file_name_list[0]}')
                        pyautogui.hotkey('ctrl', 'V', interval=0.2)
            messsure_deatil_cofig = '1'

        if messure_project_cofig == '':
            config_2 = connect_messure_mode[6:]
            pyautogui.moveTo(t2[0], t2[1], duration=0.5)
            pyautogui.click()
            if check_project_status == '':
                for i in range(len(cells_coord[0])):
                    pyautogui.moveTo(cells_coord[0][i][0] + left, cells_coord[0][i][1] + top, duration=0.5)
                    pyautogui.click()
                    check_project_status = '1'
            else:
                for i in range(len(cells_coord[0])):
                    pyautogui.moveTo(cells_coord[0][i][0] + left, cells_coord[0][i][1] + top, duration=0.5)
                    pyautogui.click()
                    pyautogui.sleep(1.0)
                    pyautogui.click()
                    
            for i in range(len(config_2)):
                if config_2[i] != '':
                    if i == 38 or i == 39:
                        pyautogui.moveTo(cells_coord[1][i+6][0] + left, cells_coord[1][i+6][1] + top, duration=0.5)
                        pyautogui.doubleClick()
                        pyautogui.moveTo(cells_coord[1][i+6][0] + left, cells_coord[1][i+6][1] + top + 20, duration=0.5)
                        value = config_2[i]
                        if value == '50':
                            pyautogui.scroll(start_and_stop_rows[value][0])
                            pyautogui.sleep(0.2)
                            pyautogui.scroll(start_and_stop_rows[value][1])
                            pyautogui.sleep(0.2)
                            pyautogui.click()
                        else:
                            offset = start_and_stop_rows[value][1]
                            pyautogui.moveTo(
                                cells_coord[1][i+6][0] + left,
                                cells_coord[1][i+6][1] + top + offset, duration=0.5)
                            pyautogui.click()
                    else:
                        pyautogui.moveTo(cells_coord[1][i+6][0] + left, cells_coord[1][i+6][1] + top, duration=0.5)
                        pyautogui.click()
            messure_project_cofig = '1'
        
        if messsure_deatil_cofig == '0':
            if auto_save_file == '0':
                pyautogui.moveTo(cells_coord[1][5][0] + left, cells_coord[1][5][1] + top, duration=0.5)
                pyautogui.click()
                pyautogui.hotkey('ctrl', 'a', interval=0.5)
                pyperclip.copy(save_file_name)
                pyautogui.hotkey('ctrl', 'V', interval=0.5)

            messsure_deatil_cofig = '1'

    if  messure_project_cofig == '1' and messsure_deatil_cofig == '1':
        parm_dict_set = {}
        win32gui.EnumChildWindows(deatil_messure_set_handle, lambda hwnd, parm: parm.update({hwnd:win32gui.GetWindowText(hwnd)}), parm_dict_set)
        if "应用" in parm_dict_set.values():
            key_child_setting = list(parm_dict_set.keys())[list(parm_dict_set.values()).index('确认')]
            left, top, right, bottom = win32gui.GetWindowRect(key_child_setting)
            pyautogui.moveTo(left + (right - left) / 2, top + (bottom - top) / 2, duration=0.5)
            pyautogui.click()
            pyautogui.sleep(10)
        messure_status = '1'
