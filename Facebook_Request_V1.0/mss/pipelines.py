# -*- coding: utf-8 -*-

import json,codecs,os,time,csv,psycopg2,datetime
from mss.items import AccountItem, FriendsItem, LikeItem
from mss.settings import COLOR


class FacebookPipeline(object):
    
    red = "\033[31;1m  %s  \033[0m"
    blue = "\033[34;1m  %s  \033[0m"
    green = "\033[1;32;40m  %s  \033[0m"
    yellow = "\033[33;1m  %s  \033[0m"
    
    def __init__(self):
        self.num = 0
        self.collect_about_num = 0
    
    def process_item(self, item, spider):
        #write file or db
        print "in pipeline........."
        print self.green % json.dumps(dict(item), ensure_ascii=False, indent=4)