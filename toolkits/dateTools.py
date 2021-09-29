# -*- coding: utf-8 -*-
import datetime
import time
from dateutil.relativedelta import relativedelta


class DateConvert:

    @staticmethod
    def get_now():
        return datetime.datetime.now()

    @staticmethod
    def TimeStampToTime(timestamp):
        time_struct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)

    @staticmethod
    def date_calc(date1, date2, diff_date):
        '''
        比较两个时间近似时间差，默认前后浮动2小时
        :param date1:
        :param date2:
        :param diff_date: {'unit': unit, 'val': val}
        :return: True，False
        '''
        if date1 > date2:
            date_before = date2
            date_after = date1
        else:
            date_before = date1
            date_after = date2
        diff_date = {'unit': diff_date[-1].lower(), 'val': int(diff_date[:-1])}
        if diff_date['unit'] == 'd':
            date_check = date_before + relativedelta(days=diff_date['val'])
        elif diff_date['unit'] == 'w':
            date_check = date_before + relativedelta(weeks=diff_date['val'])
        else:
            date_check = date_before + relativedelta(months=diff_date['val'])

        date_check_before = date_check - relativedelta(hours=2)
        date_check_after = date_check + relativedelta(hours=2)

        if date_check_before < date_after < date_check_after:
            return True
        else:
            return False
