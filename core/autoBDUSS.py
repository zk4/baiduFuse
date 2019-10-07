import browser_cookie3
BDUSS=None
def getBDUSS():
    if not BDUSS:
        cj = browser_cookie3.chrome(domain_name='baidu.com')
        for cookie in cj:
            if cookie.name =='BDUSS':
                return cookie.value    
    return BDUSS
            