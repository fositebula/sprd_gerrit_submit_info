import datetime
import sh
import json
import csv
import requests

def get_cookie():
    res = requests.get("http://review.source.spreadtrum.com/gerrit/login/", auth=('lava', '123@afAF'))
    if res.status_code == 200:
        return res.request.headers["cookie"]

def get_info(cookie, project, branch, status, items):
    if project == "*":
        url = "http://review.source.spreadtrum.com/gerrit/changes/?q=status:{status}+branch:{branch}&n={items}&O=81".format(status=status, branch=branch, items=items)
    else:
        url = "http://review.source.spreadtrum.com/gerrit/changes/?q=status:{status}+project:{project}+branch:{branch}&n={items}&O=81".format(status=status, project=project, branch=branch, items=items)
    j_str = sh.curl(url, "--cookie", cookie).stdout
    return j_str[4:]

def str_to_data(str):
    j_data = json.loads(str)
    return j_data

def get_submit_date(data):
    date_time_str = data.get("submitted")
    date_str = date_time_str.split(" ")[0]
    return datetime.datetime.strptime(date_str, "%Y-%m-%d")

def populur_data(da):
    print da
    base_url = "http://review.source.spreadtrum.com/gerrit/#/c/{}"
    Lava_label_ap = da.get("labels").get("LAVA").get("approved")
    Lava_label_re = da.get("labels").get("LAVA").get("rejected")
    if Lava_label_ap:
        lava_label = "Y"
    elif Lava_label_re:
        lava_label = "N"
    else:
        lava_label = ""
    pjt = da.get('project')
    return (base_url.format(da.get("_number")), pjt, lava_label, '\'' + da.get("submitted"))

def get_branch_project(re_info):
    for key in re_info.keys():
        for item in re_info[key]:
            yield item["branch"], item["project"]


if __name__ == "__main__":
    cookie = get_cookie()

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
    get_cookie()
    data_to_write = []
    days = 1
    with open(csv_output, 'wb') as csv_file:
        csv_had = csv.writer(csv_file)
        csv_had.writerow(["gerritid", "project", "LAVA", "MergedTime"])
        for branch, project in get_branch_project(whitch_get):
            print "****", "branch ", branch, "project ", project
            info_str = get_info(cookie, project, branch, status, items)
            infos_data = str_to_data(info_str)
            now_date = datetime.datetime.now()

            for index, info in enumerate(infos_data):
                date = get_submit_date(info)
                if now_date - date < datetime.timedelta(days=days):
                    data_to_write.append(populur_data(info))
                    # print populur_data(info)

        csv_had.writerows(data_to_write)
