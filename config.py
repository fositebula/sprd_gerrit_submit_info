import logging

LAVA_JOIN_COMPILE_JSON = '.'

CIRCLE_TIME = 200
EXEC_TIME='10:15'
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
