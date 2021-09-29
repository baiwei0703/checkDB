import time
import requests
import json


class WeChat:
    def __init__(self, wx_info):
        self.CORPID, self.CORPSECRET, self.AGENTID = wx_info
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    # 需要传入发送信息和接受人，接收者用户名,多个用户用|分割
    def send_data(self, sendType, sendFor, message):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.access_token
        send_values = {
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0",
            "enable_duplicate_check": 1,
            "duplicate_check_interval": 1
        }
        if sendType == 'dept':
            send_values['toparty'] = sendFor
        elif sendType == 'user':
            send_values['touser'] = sendFor
        else:
            return '发送类型错误'
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        self.respone = requests.post(send_url, send_msges)
        self.respone = self.respone.json()  # 当返回的数据是json串的时候直接用.json即可将respone转换成字典
        # 写入日志
        # self.ret_write(self.respone)
        return self.respone

        # 需要传入发送信息和接受人，接收者用户名,多个用户用|分割

    def send_data_mk(self, sendType, sendFor, message):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.access_token
        send_values = {
            "msgtype": "markdown",
            "agentid": self.AGENTID,
            "markdown": {
                "content": message
            },
            "safe": "0",
            "enable_duplicate_check": 1,
            "duplicate_check_interval": 1
        }
        if sendType == 'dept':
            send_values['toparty'] = sendFor
        elif sendType == 'user':
            send_values['touser'] = sendFor
        else:
            return '发送类型错误'
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        self.respone = requests.post(send_url, send_msges)
        self.respone = self.respone.json()  # 当返回的数据是json串的时候直接用.json即可将respone转换成字典
        # 写入日志
        # self.ret_write(self.respone)
        return self.respone

    @staticmethod
    def ret_write(respone):
        cur_time = time.strftime('%Y-%m-%D %H:%M:%S', time.gmtime())
        sep = '==========\n'
        content = ''
        for k, v in respone.items():
            line = ''.join(k + ':' + str(v) + '\n')
            content += line
        with open('history.txt', 'a', encoding='utf-8') as fp:
            fp.write(sep + cur_time + '  :\n' + content)

    # 通过部门ID或部门名称，获取部门信息，默认是全公司，返回是字典
    def get_dept(self, deptId=1, deptName='百利天下教育集团'):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?id={}&access_token={}'.format(deptId,
                                                                                                      self.access_token)
        self.respone = requests.get(send_url)
        self.respone = self.respone.json()
        if deptName == '百利天下教育集团':
            return True, self.respone['department']
        for dept in self.respone['department']:
            if dept['name'] == deptName:
                return True, dept
        #         True, {'id': 327, 'name': '信息系统部', 'parentid': 61, 'order': 99999000}
        else:
            return False, '信息未查到！'

    # 通过部门ID或者部门名称，获取部门下所有成员信息，默认全公司，返回是列表套字典
    def get_dept_user(self, deptId=1, deptName='百利天下教育集团', fetch_child=1):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?&department_id={}&fetch_child={}&access_token={}'.format(
            deptId, fetch_child,
            self.access_token)
        self.respone = requests.get(send_url)
        self.respone = self.respone.json()
        if deptName == '百利天下教育集团':
            return True, self.respone['userlist']
        # 通过部门名获取部门ID
        ret_status, retDict = self.get_dept(deptName=deptName)
        if ret_status:
            ret_status, userinfo = self.get_dept_user(deptId=retDict['id'])
            return True, userinfo
        else:
            return False, '未找到！'

    # 通过人员ID或者姓名，获取企业成员信息，返回是列表套字典（可能有重名!!!）
    def get_user(self, userId=0, userName=''):
        if userId == 0 and userName == '':
            return False, '未输入查询条件！！'
        elif userId != 0 and userName == '':
            send_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?userid={}&access_token={}'.format(userId,
                                                                                                       self.access_token)
            self.respone = requests.get(send_url)
            self.respone = self.respone.json()
            return True, self.respone
        elif userId == 0 and userName != '':
            # 先获取所有人员信息
            send_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?&department_id=1&fetch_child=1&access_token={}'.format(
                self.access_token)
            self.respone = requests.get(send_url)
            all_user_list = self.respone.json()['userlist']
            # 查到所有用户后过滤对应名字
            ret = list(filter(lambda userinfo: userinfo['name'] == userName, all_user_list))
            if len(ret):
                # 因为可能有重名，所以返回值可能是一个列表套字典
                return True, ret
            # [{'userid': '12071301', 'name': '白玮', 'department': [382], 'position': '', 'mobile': '13720094924', 'gender': '1', 'email': 'baiwei@bailitop.com', 'avatar': 'http://wework.qpic.cn/wwhead/duc2TvpEgSSdsPInfahzxwd3k6b1M141PeBEYbBqNdot6NRDNR8eVjuD2csyU6wWu3N98Bb3BcA/0', 'status': 1, 'enable': 1, 'isleader': 0, 'extattr': {'attrs': [{'name': '个性签名', 'value': '', 'type': 0, 'text': {'value': ''}}]}, 'hide_mobile': 0, 'telephone': '1618', 'order': [0], 'external_profile': {'external_attr': [{'type': 1, 'name': '动态', 'web': {'url': 'http://ww1dc17f7e79437d0d.wemoment.wshmi.com/H5/moment?user_id=152080&corpid=ww1dc17f7e79437d0d', 'title': ' '}}], 'external_corp_name': ''}, 'main_department': 382, 'qr_code': 'https://open.work.weixin.qq.com/wwopen/userQRCode?vcode=vcfcbdf4a76e3d0ce8', 'alias': 'はくい', 'is_leader_in_dept': [0], 'address': '', 'thumb_avatar': 'http://wework.qpic.cn/wwhead/duc2TvpEgSSdsPInfahzxwd3k6b1M141PeBEYbBqNdot6NRDNR8eVjuD2csyU6wWu3N98Bb3BcA/100'}]
            return False, '未找到！'
        else:
            return False, '只能输入一个条件！！'

# wx_app_info = ('ww1dc17f7e79437d0d', 'SL38OAWWORtJdpfJ1pEqsfpASGhsKh7OGZV3QjVnt8U', '1000005')
# test = WeChat(wx_app_info)
# dept_list = test.get_dept(deptName='信息系统部')
# print(dept_list)

# dept_user_list = test.get_dept_user(deptName='信息系统部')
# print(dept_user_list[1])

# status, user = test.get_user(userName='白玮')
# print(user)
# msg = "尊敬的***name***老师:\n" \
#       ">您今日数据共享平台的**密码**为:\n" \
#       "<font color=\"info\">pwd</font>\n" \
#       "`请谨慎保管使用!`\n" \
#       "<font color=\"comment\">P.S. 除使用密码登录外，同时支持企业微信扫码登录。</font>".replace(
#     'name', '白玮')
# res_user = test.send_data_mk(sendType='user', sendFor='12071301', message=msg)
# print(res_user)

# res_dept = test.send_data(sendType='dept', sendFor='382', message='这是一次测试')
# print(res_dept)
