import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    'Referer': 'http://sso.jwc.whut.edu.cn/Certification/toLogin.do',
}
class_type_list = ['专业必修', "通识必修", "大类必修", "英语必修", "体育必修"]


def signIN_sso(sno, password):
    url_log = 'http://sso.jwc.whut.edu.cn/Certification/login.do'
    post_data = {
        'userName': sno,
        'password': password,
        'type': 'xs',
        'xmlmsg': '',
        'systemId': ''
    }
    s = requests.Session()
    s.post(url_log, data=post_data, headers=headers)
    s.close()
    return s.cookies


def get_snkey(cookies):
    s = requests.session()
    s.cookies = cookies
    score_url = "http://202.114.90.180/Score"
    snkey_page = s.get(url=score_url, headers=headers)
    soup = BeautifulSoup(snkey_page.text, "html.parser")
    snkey = soup.find_all("ul", "tree treeFolder")[0].find_all('a')[1]['href'][18:]
    s.close()
    return snkey


def get_data(cookies, snkey, sno):
    headers['Referer'] = "http://202.114.90.180/Score/login.do"
    score_url = "http://202.114.90.180/Score/lscjList.do"
    post_data = {
        'pageNum': '1',
        'numPerPage': '200',
        'xh': sno,
        'xn': '2017-2018',
        'xnxq': '',
        'nj': '',
        "xydm": '',
        "zydm": "",
        "bjmc": "",
        "kcmc": "",
        "kcdm": "",
        "xslb": "",
        "kcxz": "",
        "jsxm": "",
        "snkey": snkey
    }
    s = requests.session()
    s.cookies = cookies
    score_page = s.post(url=score_url, headers=headers, data=post_data)
    soup = BeautifulSoup(score_page.text, "html.parser")
    score_list = soup.find_all("tr")[2:]
    class_list = []
    all_point = 0.0
    all_score = 0.0
    class_set = set()
    for cls in score_list:
        td_list = cls.find_all('td')
        class_id = td_list[1].text
        if class_id in class_set:
            continue
        else:
            class_set.add(class_id)
        class_name = td_list[2].text
        class_type = td_list[4].text
        if class_type not in class_type_list:
            continue
        class_point = td_list[5].text
        class_score = td_list[6].text
        all_point = all_point + float(class_point)
        if class_score == "优秀":
            all_score = all_score + 95 * float(class_point)
        elif class_score == '良好':
            all_score = all_score + 85 * float(class_point)
        elif class_score == '一般':
            all_score = all_score + 75 * float(class_point)
        elif class_score == "及格":
            all_score = all_score + 65 * float(class_point)
        elif class_score == "不及格":
            all_score = all_score
        else:
            all_score = all_score + float(class_score) * float(class_point)
        add_ret = {
            "name": class_name,
            "type": class_type,
            "point": class_point,
            "score": class_score
        }
        class_list.append(add_ret)
    gpa = all_score // all_point
    ret = {
        "gpa": gpa,
        "point": all_point,
        "score_sum": all_score,
        "list": class_list
    }
    return ret


def form_json(data):
    return json.dumps(data)


def sso_main(sno, password):
    ret=""
    errCode=200
    errMsg=""
    try:
        cookies = signIN_sso(sno, password)
        snkey = get_snkey(cookies)
        data = get_data(cookies, snkey, sno)
        ret=data
    except:
        errCode=500
        errMsg="不知道出现了什么问题反正肯定不是我代码的问题2333，你可以尝试看一下教务处能不能登陆，如果能登陆的话再来试一试"
    retData={
        "errCode":errCode,
        "errMsg":errMsg,
        "data":ret
    }
    return form_json(retData)
