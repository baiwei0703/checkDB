# -*- coding: utf-8 -*-
from toolkits.DButils import MyPymysqlPool
from toolkits.dateTools import DateConvert as dc
from toolkits.fileTools import GetFileInfo as gf


if __name__ == '__main__':
    db = MyPymysqlPool('db_168_test')
    check_sql = f"select id,filePath,copyPeriod,remarks from dbBack_info where isEnabled = 1"
    task_list = db.get_all(sql=check_sql)
    now_time = dc.get_now()
    for task in task_list:
        get_last_info = f"select checkDatetime,folderSize,fileNumber from dbBack_history where taskId = {task['id']} and isNormal = 1 order by id desc"
        # 获取上次文件备份的信息
        last_info = db.get_one(sql=get_last_info)
        folderSize = gf.get_dir_size(task['filePath'])
        fileInfo = gf.get_dir_file_number(task['filePath'])
        isNormal = 1
        errorResson = ''
        # 如果有上次记录，则进行对比。没有则直接记录
        if last_info:
            if gf.check_path_exist(task['filePath']):
                if abs(folderSize - task['folderSize']) / task['folderSize'] > 0.05:
                    errorResson += '备份文件目录大小异常'
                if len(fileInfo['file_num']) != task['fileNumber']:
                    errorResson += '备份文件目录数量异常'
                mtime_check = []
                for fileName in fileInfo['file_list']:
                    fileMtime = gf.get_file_mtime(task['filePath'], fileName)
                    if dc.date_calc(fileMtime, task['checkDatetime'], task['copyPeriod']):
                        mtime_check.append(1)
                if not mtime_check:
                    errorResson += '没有生成任何备份文件'
            else:
                errorResson = '文件夹不存在'
            if errorResson:
                isNormal = 0
        ins_check_ret_sql = f"insert into dbBack_history(taskId, checkDatetime, folderSize, fileNumber, isNormal, errorResson) value (%s,%s,%s,%s,%s,%s,%s)"
        data = [task['id'], now_time, folderSize, fileInfo['fileNumber'], isNormal, errorResson]
        db.insert(ins_check_ret_sql, data)
