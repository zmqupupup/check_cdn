import dns.resolver
import re
import json
# cname 列表
cdn_cname_list = []
# cdn 具体信息
cdn_info = []

# 读取文件
def load_file(path):
    with open(path, "r+", encoding="utf-8") as f:
        return f.readlines()

# 初始化列表
def init_cdn_info():
    global cdn_cname_list, cdn_info
    if not cdn_info:
        cdn_cname_list = []
        data = "\n".join(load_file("cdn_cname.json"))
        cdn_info = json.loads(data)

        for item in cdn_info:
            cdn_cname_list.extend(item["cname_domain"])

def cname_in_cname_list(cname):
    for item in cdn_cname_list:
        if cname.endswith("." + item):
            return True
    else:
        return False

def get_cdn_name_by_cname(cname):
    try:
        init_cdn_info()
        if not cname_in_cname_list(cname):
            return ""
        for item in cdn_info:
            for target in item["cname_domain"]:
                if cname.endswith("." + target):
                    return item["name"]
    except Exception as e:
        return ""

def cdn_check(domain):
    """
    如果有 cdn 返回 true
    如果没有 cdn 返回 false
    """
    ipcount = 0
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['114.114.114.114', '202.100.96.68']
        domain = domain.strip()
        a = resolver.resolve(domain, 'A')
        for index, value in enumerate(a.response.answer):
            for j in value.items:
                if re.search(r'\d+\.\d+\.\d+\.\d+', j.to_text()):
                    ipcount += 1
                    if ipcount >= 2:
                        return True, domain
                elif re.search(r'(\w+\.)+', j.to_text()):
                    cname = j.to_text()[:-1]
                    p1 = '.'.join(cname.split('.')[-2:])
                    p2 = '.'.join(domain.split('.')[-2:])
                    if p1 == p2:
                        return False, domain
                    else:
                        cdn_name = get_cdn_name_by_cname(cname)
                        return True,cdn_name,domain

                else:
                    return False, domain
        if ipcount == 1:
            return False, domain
    except Exception as e:
        return None, domain


if __name__ == "__main__":
    print(cdn_check("www.baidu.com"))