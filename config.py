import logging

LAVA_JOIN_COMPILE_JSON = '.'

CIRCLE_TIME = 50
EXEC_TIME='00:15'
KEY = "pythonge"
LOG_FILE = "gerritinfo.log"
LOG_LEVEL = logging.INFO
logger = logging.getLogger(__name__)
USER = "dongpl"
USER_PASSWD = "dongpl123"
DAYS = 1
LOGIN_INFO = "login.info"
VERIFY_LAVA_PROJECTS = 'apuser@10.0.70.54:/home/apuser/tjxt/lavaWhiteList/joint_complie.json'
# VERIFY_LAVA_PROJECTS = 'apuser@10.0.70.54:/home/apuser/joint_complie.json'
CONTEXT = {
    "loginfo":False,
    "loginfo_content":False,
    "query_type":"updated",
}



TO_SOMEONE = ["dongpl@spreadst.com", "yanqi.zhang@unisoc.com"]
MAIL_ACCOUNT = "pl.dong@spreadtrum.com"
PASSWD = "123@ffff"
MAIL_FROM = "Gerrit Info <pl.dong@unisoc.com>"
SMPT_HOST = "smtp.unisoc.com"
SMPT_PORT = 587
DOCMD = "ehlo"