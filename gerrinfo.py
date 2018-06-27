# -*- coding: utf-8 -*-
import datetime
import json
import csv
import os
import traceback

import schedule

import requests
import time

import sh

from config import *

class PermissionException(Exception):
    pass


class DaysException(Exception):
    pass

def logger_init():
    logger.setLevel(level = LOG_LEVEL)
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def session():
    logger.info(USER+"**********"+USER_PASSWD)
    url = 'http://review.source.spreadtrum.com/gerrit/login/'
    s = requests.Session()
    res = s.get(url, auth=(USER, USER_PASSWD))
    if '4' in str(res.status_code):
        raise PermissionException
    return s

def get_info(s, project, branch, status, items):
    CONTEXT["loginfo_content"] = True
    if status == "":
        url = "http://review.source.spreadtrum.com/gerrit/changes/?q=project:{project}+branch:{branch}&n={items}&O=81".format(\
            project=project, branch=branch, items=items)
    elif project == "*":
        url = "http://review.source.spreadtrum.com/gerrit/changes/?q=status:{status}+branch:{branch}&n={items}&O=81".format(status=status, branch=branch, items=items)
    else:
        url = "http://review.source.spreadtrum.com/gerrit/changes/?q=status:{status}+project:{project}+branch:{branch}&n={items}&O=81".format(status=status, project=project, branch=branch, items=items)
    res = s.get(url)
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
    gerrit_status = da.get("status")
    logger.info(da)
    if CONTEXT['query_type'] == "":
        submitted_time = da.get("updated")
    elif CONTEXT['query_type'] == "merged":
        submitted_time = da.get("submitted")
    ltime = to_local_time(submitted_time.split('.')[0])
    ldate_time = datetime.datetime.strftime(ltime, "%Y-%m-%d %H:%M:%S")

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
    for info in re_info:
        branch = info['branch_name']
        bproject = info['bproject']
        for bjt in bproject:
            time.sleep(CIRCLE_TIME)
            yield branch, bjt

def get_time_stamp():
    ltime = time.localtime()
    return time.strftime("%Y%m%d%H%M%S", ltime)


def job():
    items = 100
    status = ""
    CONTEXT['query_type'] = status
    csv_output = "gerritinfo_%s.csv"%get_time_stamp()
    data_to_write = []
    days = DAYS
    try:
        j_data = get_from_json()
        logger.info(j_data)
        if j_data:
            s = session()
            for branch, project in get_branch_project(j_data):
                logger.info("****"+"branch: "+branch+"*****"+"project: "+project)
                logger.info( "**** "+ "branch "+branch+" project "+ project)
                info_str = get_info(s, project, branch, status, items)
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
    except:
        logger.info(traceback.format_exc())

def _get_white_list_from_54():
    sh.scp([VERIFY_LAVA_PROJECTS, '.'])
    if os.path.exists('./joint_complie.json'):
        return 'ok'
    else:
        return 'suc'

def get_from_json():
    ret = _get_white_list_from_54()
    if ret == 'ok':
        with open('joint_complie.json') as fd:
            j_str = fd.read()
            j_data = json.loads(j_str)
            return j_data
    else:
        return None


if __name__ == "__main__":
    logger_init()
    logger.info(EXEC_TIME)
    schedule.every().day.at(EXEC_TIME).do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
