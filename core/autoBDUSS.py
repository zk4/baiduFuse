import browser_cookie3
BDUSS=None
cj = browser_cookie3.chrome(domain_name='baidu.com')
def getBDUSS():
    if not BDUSS:
        for cookie in cj:
            if cookie.name =='BDUSS':
                return cookie.value    
    return BDUSS
            