# -*- coding: utf-8 -*-
import os
from os.path import join, getsize
from toolkits.dateTools import DateConvert as dc


class GetFileInfo:

    @staticmethod
    def check_path_exist(dir_full_path):
        '''
        检查文件路径是否存在
        :param dir_full_path: 文件夹全路径
        :return: True为存在
        '''
        if os.path.exists(dir_full_path):
            return True
        return False

    @staticmethod
    def get_file_ize(file_full_path):
        fsize = os.path.getsize(file_full_path)
        fsize = fsize / float(1024 * 1024)
        return round(fsize, 2)

    @staticmethod
    def get_dir_size(dir_full_path):
        '''
        查询某一个文件夹的总大小
        :param dir_full_path: 文件夹全路径
        :return: 以兆字节为单位的大小，字符型
        '''
        size = 0
        for root, dirs, files in os.walk(dir_full_path):
            size += sum([getsize(join(root, name)) for name in files])
        return "%.2f" % float(size / 1024 / 1024)

    @staticmethod
    def get_dir_file_number(dir_full_path):
        '''
        查询某一个文件夹中文件个数及文件列表
        :param dir_full_path: 文件夹全路径
        :return: {'file_num':file_num, 'file_list':file_list}
        '''
        file_list = os.listdir(dir_full_path)
        file_num = len(file_list)
        return {'file_num': file_num, 'file_list': file_list}

    @staticmethod
    def get_file_mtime(file_path, file_name):
        '''
        获取每个文件的修改时间
        :param file_path: 文件路径
        :param file_name: 文件名
        :return: 返回文件的修改时间，
        '''
        mtime = os.path.getmtime(os.path.join(file_path, file_name))
        return dc.TimeStampToTime(mtime)
