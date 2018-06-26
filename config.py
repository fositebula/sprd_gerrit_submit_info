import logging

LAVA_JOIN_COMPILE_JSON = '.'

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
