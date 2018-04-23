# -*- coding: utf-8 -*-
import datetime
import json
import csv
import os
import traceback

import requests
import logging
import time
from tkinter import *
from tkinter.messagebox import *
from binascii import b2a_hex, a2b_hex
from Crypto.Cipher import DES

KEY = "pythonge"
LOG_FILE = "gerritinfo.log"
LOG_LEVEL = logging.INFO
logger = logging.getLogger(__name__)
USER = ""
USER_PASSWD = ""
DAYS = 1
LOGIN_INFO = "login.info"
CONTEXT = {
    "loginfo":False,
    "loginfo_content":False,
    "query_type":"updated",
}

class PermissionException(Exception):
    pass


class DaysException(Exception):
    pass


class LoginPage(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.username = StringVar()
        self.password = StringVar()
        self.days = StringVar()
        self.pack()
        self.createForm()

    def createForm(self):
        Label(self, text='注：默认只需输入天数', bg='red').grid(row=0, stick=W, pady=10)
        Label(self, text='账户: ').grid(row=2, stick=W, pady=10)
        Entry(self, textvariable=self.username).grid(row=2, column=1, stick=E)
        Label(self, text='密码: ').grid(row=3, stick=W, pady=10)
        Entry(self, textvariable=self.password, show='*').grid(row=3, column=1, stick=E)
        Label(self, text='前几天（max=7）？: ').grid(row=4, stick=W, pady=2)
        Entry(self, textvariable=self.days).grid(row=4, column=1, stick=E)
        Button(self, text='登录', command=self.loginCheck).grid(row=6, stick=W, pady=10)
        Button(self, text='退出', command=self.quit).grid(row=6, column=1, stick=E)

    def loginCheck(self):
        global USER, USER_PASSWD, DAYS
        user = self.username.get()
        passwd = self.password.get()
        print "***", user, passwd
        if (CONTEXT["loginfo"] == True and CONTEXT["loginfo_content"] == False) and user != "" and passwd != "":
            USER = user
            USER_PASSWD = passwd
            save_login_info(USER, USER_PASSWD)
        try:
            DAYS = int(self.days.get())
            if DAYS == 0:
                showinfo(title='错误', message='请输入正确的天数！')
                raise DaysException
            main()
            showinfo(title='成功', message='获取完成！')
            self.quit()
        except PermissionException:
            if CONTEXT["loginfo"]:
                CONTEXT["loginfo_content"] = False
            showinfo(title='错误', message='账号或密码错误！')
            print('账号或密码错误！')
        except DaysException:
            print traceback.print_exc()
            showinfo(title='错误', message='请输入正确的天数！')
            print('请输入正确的天数！')


def logger_init():
    logger.setLevel(level = LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_info(project, branch, status, items):
    print "@@@", USER, USER_PASSWD
    res = requests.get("http://review.source.spreadtrum.com/gerrit/login/", auth=(USER, USER_PASSWD))
    header = res.request.headers
    print  res.status_code
    if res.status_code == 200:
        CONTEXT["loginfo_content"] = True
        if status == "":
            url = "http://review.source.spreadtrum.com/gerrit/changes/?q=project:{project}+branch:{branch}&n={items}&O=81".format(\
                project=project, branch=branch, items=items)
        elif project == "*":
            url = "http://review.source.spreadtrum.com/gerrit/changes/?q=status:{status}+branch:{branch}&n={items}&O=81".format(status=status, branch=branch, items=items)
        else:
            url = "http://review.source.spreadtrum.com/gerrit/changes/?q=status:{status}+project:{project}+branch:{branch}&n={items}&O=81".format(status=status, project=project, branch=branch, items=items)
        res = requests.get(url, headers=header)
    elif res.status_code == 401:
        raise PermissionException("No Permission")
    return res.content[4:]

def str_to_data(str):
    j_data = json.loads(str)
    return j_data

def to_local_time(time_str):
    ltime_s = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S')) + 8*60*60
    ltime_d = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ltime_s))
    return datetime.datetime.strptime(ltime_d, "%Y-%m-%d %H:%M:%S")

def get_submit_date(data):
    date_time_str = data.get("submitted")
    date_str = date_time_str.split(".")[0]
    return to_local_time(date_str)

def get_updated_date(data):
    date_time_str = data.get("updated")
    date_str = date_time_str.split(".")[0]
    return to_local_time(date_str)

def populur_data(da):
    print da
    gerrit_status = da.get("status")
    logger.info(da)
    if CONTEXT['query_type'] == "":
        submitted_time = da.get("updated")
    elif CONTEXT['query_type'] == "merged":
        submitted_time = da.get("submitted")
    ltime = to_local_time(submitted_time.split('.')[0])
    ldate_time = datetime.datetime.strftime(ltime, "%Y-%m-%d %H:%M:%S")
    print ldate_time

    lava_label = ""
    verify_label = ""
    verifyer = ""
    if gerrit_status != "ABANDONED":
        verifyera = da.get("labels").get("Verified").get("approved")
        verifyerr = da.get("labels").get("Verified").get("rejected")

        if verifyera:
            verify_label = "\'+1"
            verifyer = verifyera.get("username")
        elif verifyerr:
            verify_label = "\'-1"
            verifyer = verifyerr.get("username")
        else:
            verify_label = ""
            verifyer = ""

        Lava_label_ap = da.get("labels").get("LAVA").get("approved")
        Lava_label_re = da.get("labels").get("LAVA").get("rejected")
        Lava_label_di = da.get("labels").get("LAVA").get("disliked")
        if Lava_label_ap:
            lava_label = "\'+1"
        elif Lava_label_re:
            lava_label = "\'-3"
        elif Lava_label_di:
            lava_label = "\'-1"
        else:
            lava_label = ""

    pjt = da.get('project')
    owner_email = da.get('owner').get('email')
    brh = da.get('branch')

    base_url = "http://review.source.spreadtrum.com/gerrit/#/c/{}"
    return (base_url.format(da.get("_number")), pjt, brh, owner_email, verifyer, verify_label, lava_label, '\'' + ldate_time, gerrit_status)


def get_branch_project(re_info):
    for key in re_info.keys():
        for item in re_info[key]:
            yield item["branch"], item["project"]

def get_time_stamp():
    ltime = time.localtime()
    return time.strftime("%Y%m%d%H%M%S", ltime)


def main():
    whitch_get = {
        "kernel":[{"branch":"sprdlinux4.4", "project":"kernel/common"}],
        "uboot":[{"branch":"sprduboot64_v201507","project":"u-boot15"}],
        "chipram":[{"branch":"sprdchipram16", "project":"chipram"}, {"branch":"sprdroid6.0_whale_dev", "project":"chipram"}],
        "tos":[{"branch":"sprd_trusty", "project":"*"}],
        "sml":[{"branch":"sprdatf-1.3", "project":"whale_security/ATF/arm-trusted-firmware-1.3"}, {"branch":"sprdatf-1.4", "project":"whale_security/ATF/arm-trusted-firmware"}],
    }

    items = 100
    status = "merged"
    CONTEXT['query_type'] = status
    csv_output = "gerritinfo_%s.csv"%get_time_stamp()
    data_to_write = []
    days = DAYS
    for branch, project in get_branch_project(whitch_get):
        print "****", "branch ", branch, "project ", project
        logger.info( "**** "+ "branch "+branch+" project "+ project)
        info_str = get_info(project, branch, status, items)
        infos_data = str_to_data(info_str)
        now_date = datetime.datetime.now().date()

        for index, info in enumerate(infos_data):
            if status == "":
                _date = get_updated_date(info)
            elif status == "merged":
                _date = get_submit_date(info)
            if days == 1:
                yesterday = now_date - datetime.timedelta(days=days)
                if yesterday != _date.date():
                    continue
            elif days > 1:
                if ((now_date - _date.date()) > datetime.timedelta(days=days))\
                        or ((now_date - _date.date()) <= datetime.timedelta(days=0)):
                    continue

            data_to_write.append(populur_data(info))
    with open(csv_output, 'wb') as csv_file:
        csv_had = csv.writer(csv_file)
        if CONTEXT['query_type'] == "":
            csv_had.writerow(["gerritid", "project", "branch", "owner", "verify user name", "verify label", "LAVA", "UpDatedTime", "gerrit status", "备注"])
        elif CONTEXT['query_type'] == "merged":
            csv_had.writerow(["gerritid", "project", "branch", "owner", "verify user name", "verify label", "LAVA", "MergedTime", "gerrit status", "备注"])

        csv_had.writerows(data_to_write)

def windows():
    root = Tk()
    root.title('GerritInfo')
    width = 280
    height = 200
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(alignstr)

    page1 = LoginPage()
    root.mainloop()

def check_login_info():
    global USER_PASSWD, USER
    obj = DES.new(KEY)
    file_exists = os.path.exists(LOGIN_INFO)
    CONTEXT["loginfo"] = True
    if file_exists:
        with open(LOGIN_INFO, 'rb') as fd:
            info_str = fd.read()
            info_data = json.loads(info_str)
            get_cryp = a2b_hex(info_data["passwd"])
            USER_PASSWD = remove_space_key(obj.decrypt(get_cryp))
            get_cryp = a2b_hex(info_data["user"])
            USER = remove_space_key(obj.decrypt(get_cryp))
            pass

def append_space_key(s):
    sl = 8 - len(s)%8
    return s + " "*sl

def remove_space_key(s):
    return s.strip()

def save_login_info(user, passwd):
    global LOGIN_INFO
    if  user != "" and passwd != "":
        users = append_space_key(user)
        passwds = append_space_key(passwd)
        print users, passwds
        obj = DES.new(KEY)
        cryp = obj.encrypt(users)
        su = b2a_hex(cryp)
        cryp = obj.encrypt(passwds)
        sp = b2a_hex(cryp)
        with open(LOGIN_INFO, 'w') as fd:
            s = json.dumps({"passwd":sp, "user":su})
            fd.write(s)

if __name__ == "__main__":
    check_login_info()
    logger_init()
    windows()
