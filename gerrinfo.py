# -*- coding: utf-8 -*-
import datetime
import json
import csv
import requests
import logging
import time
from tkinter import *
from tkinter.messagebox import *

LOG_FILE = "gerritinfo.log"
LOG_LEVEL = logging.INFO
logger = logging.getLogger(__name__)
USER = ""
USER_PASSWD = ""

class PermissionException(Exception):
    pass


class LoginPage(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.username = StringVar()
        self.password = StringVar()
        self.pack()
        self.createForm()

    def createForm(self):
        Label(self).grid(row=0, stick=W, pady=10)
        Label(self, text='账户: ').grid(row=1, stick=W, pady=10)
        Entry(self, textvariable=self.username).grid(row=1, column=1, stick=E)
        Label(self, text='密码: ').grid(row=2, stick=W, pady=10)
        Entry(self, textvariable=self.password, show='*').grid(row=2, column=1, stick=E)
        Button(self, text='登录', command=self.loginCheck).grid(row=3, stick=W, pady=10)
        Button(self, text='退出', command=self.quit).grid(row=3, column=1, stick=E)

    def loginCheck(self):
        global USER, USER_PASSWD
        USER = self.username.get()
        USER_PASSWD = self.password.get()
        try:
            main()
            self.quit()
        except PermissionException:
            showinfo(title='错误', message='账号或密码错误！')
            print('账号或密码错误！')

def logger_init():
    logger.setLevel(level = LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_info(project, branch, status, items):
    print USER, USER_PASSWD
    res = requests.get("http://review.source.spreadtrum.com/gerrit/login/", auth=(USER, USER_PASSWD))
    header = res.request.headers
    print  res.status_code
    if res.status_code == 200:
        if project == "*":
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

def populur_data(da):
    print da
    logger.info(da)
    base_url = "http://review.source.spreadtrum.com/gerrit/#/c/{}"
    Lava_label_ap = da.get("labels").get("LAVA").get("approved")
    Lava_label_re = da.get("labels").get("LAVA").get("rejected")
    submitted_time = da.get("submitted")
    ltime = to_local_time(submitted_time.split('.')[0])
    ldate_time = datetime.datetime.strftime(ltime, "%Y-%m-%d %H:%M:%S")
    print ldate_time
    if Lava_label_ap:
        lava_label = "Y"
    elif Lava_label_re:
        lava_label = "N"
    else:
        lava_label = ""
    pjt = da.get('project')
    owner_email = da.get('owner').get('email')
    brh = da.get('branch')
    return (base_url.format(da.get("_number")), pjt, brh, owner_email, lava_label, '\'' + ldate_time)

def get_branch_project(re_info):
    for key in re_info.keys():
        for item in re_info[key]:
            yield item["branch"], item["project"]

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
    csv_output = "gerritinfo.csv"
    data_to_write = []
    days = 1
    with open(csv_output, 'wb') as csv_file:
        csv_had = csv.writer(csv_file)
        csv_had.writerow(["gerritid", "project", "branch", "owner", "LAVA", "MergedTime", "备注"])
        for branch, project in get_branch_project(whitch_get):
            print "****", "branch ", branch, "project ", project
            logger.info( "**** "+ "branch "+branch+" project "+ project)
            info_str = get_info(project, branch, status, items)
            infos_data = str_to_data(info_str)
            now_date = datetime.datetime.now().date()

            for index, info in enumerate(infos_data):
                date = get_submit_date(info)
                yesterday = now_date - datetime.timedelta(days=days)
                if yesterday != date.date():
                    continue
                data_to_write.append(populur_data(info))

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

if __name__ == "__main__":

    logger_init()
    windows()