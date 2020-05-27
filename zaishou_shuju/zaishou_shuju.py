#导包
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import json
import time

#伪造设置浏览器请求头user-agent
head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
starturl_list = [
                 'https://tj.lianjia.com/ershoufang/'
                ]

#获取县级市的url
def get_cityurls(url):
    request = requests.get(url,headers=head)
    request.encoding = 'utf-8'
    soup = BeautifulSoup(request.text,'html.parser')
    cityurls = []
    prenews = soup.select('div.position>dl>dd>div>div>a')
    pre_news =  ''.join([str(i) for i in prenews])
    nameslist = re.findall("ershoufang/[a-zA-Z0-9]+/. t",pre_news)
    namesliststrip = [i.lstrip('ershoufang/').rstrip('" t')  for i in nameslist]
    k = len(namesliststrip)
    i = 0
    for i in range(k):
        newcity = url + '{}'.format(namesliststrip[i])
        cityurls.append(newcity)
        i += 1
    return cityurls

#获取二手房每一页的url
def get_pageurls(url):
    request = requests.get(url,headers=head)
    request.encoding = 'utf-8'
    soup = BeautifulSoup(request.text,'html.parser')
    totalnum = json.loads(soup.find('div',{'class':"page-box house-lst-page-box"}).get('page-data'))['totalPage']+1
    pageurls_list = []
    pageurls_list.append(url)
    for num in range(2,totalnum):
        newurl = url + 'pg{}/'.format(num)
        pageurls_list.append(newurl)
    return pageurls_list


#获取每一页的二手房url
def get_eachurls(url):
    eachurl_list = []
    request = requests.get(url,headers=head)
    request.encoding = 'utf-8'
    soup = BeautifulSoup(request.text,'html.parser')
    address_a = soup.select('li > div.info > div.title>a')
    for i in address_a:
        eachurl_list.append(i['href'])
    return eachurl_list


def news_ershoufang(url):
    data_all = []
    res = requests.get(url, headers=head)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    pre_data = soup.select('div.content > ul > li')
    pre_datanews = ''.join([str(i) for i in pre_data])
    # 城市
    data_all.append('天津')


    # 小区名字
    names = soup.select('div.communityName >a.info')
    if len(names) == 0:
        data_all.append('None')
    else:
        data_all.append(names[0].text)

    # 室厅厨卫
    shi = re.findall(u"房屋户型</span>.+所在楼层", pre_datanews)
    if len(shi) == 0:
        data_all.append('None')
    else:
        shi_news = shi[0].lstrip('房屋户型</span>').rstrip('</li><li><span class="label">所在楼层')
        data_all.append(shi_news)

    # 高度与楼层
    floor = re.findall(u"所在楼层</span>.+</li><li><span class=.label.>建筑面积", pre_datanews)
    if len(floor) == 0:
        data_all.append('None')
    else:
        floor_news = floor[0].lstrip('所在楼层</span>').rstrip('</li><li><span class="label">建筑面积')
        data_all.append(floor_news)

    # 建筑面积
    area = re.findall(u"建筑面积</span>.+户型结构", pre_datanews)
    if len(area) == 0:
        data_all.append('None')
    else:
        area_news = area[0].lstrip('建筑面积</span>').rstrip('</li><li><span class="label">户型结构')
        data_all.append(area_news)

    # 户型结构
    huxing = re.findall(u"户型结构</span>[\u4e00-\u9fa5]+</li>", pre_datanews)
    if len(huxing) == 0:
        data_all.append('None')
    else:
        huxing_news = huxing[0].lstrip('户型结构</span>').rstrip('</li>')
        data_all.append(huxing_news)

    # 套内面积
    home_area = re.findall(
        u"套内面积</span>.+<li><span class=.label.>建筑类型|套内面积</span>[\u4e00-\u9fa5]+<li><span class=.label.>建筑类型",
        pre_datanews)
    if len(home_area) == 0:
        data_all.append('None')
    else:
        home_areanews = home_area[0].lstrip('套内面积</span>').rstrip('<li><span class="label">建筑类型').rstrip('</')
        data_all.append(home_areanews)

    # 建筑类型
    label = re.findall(
        u"建筑类型</span>.+</li><li><span class=.label.>房屋朝向|建筑类型</span>[\u4e00-\u9fa5]+</li><li><span class=.label.>房屋朝向",
        pre_datanews)
    if len(label) == 0:
        data_all.append('None')
    else:
        label_news = label[0].lstrip('建筑类型</span>').rstrip('</li><li><span class="label">房屋朝向')
        data_all.append(label_news)

    # 房屋朝向
    direction = re.findall(u"房屋朝向</span>[\u4e00-\u9fa5]+</li><li><span class=.label.>建筑结构", pre_datanews)
    if len(direction) == 0:
        data_all.append('None')
    else:
        direction_news = direction[0].lstrip('房屋朝向</span>').rstrip('</li><li><span class="label">建筑结构')
        data_all.append(direction_news)

    # 建成年代
    com_time = 'None'
    data_all.append(com_time)

    # 装修情况
    fitment = re.findall(u"装修情况</span>[\u4e00-\u9fa5]+</li><li>", pre_datanews)
    if len(fitment) == 0:
        data_all.append('None')
    else:
        fitment_news = fitment[0].lstrip('装修情况</span>').rstrip('</li><li>')
        data_all.append(fitment_news)

    # 建筑结构
    building = re.findall(u"建筑结构</span>[\u4e00-\u9fa5]+</li><li><span", pre_datanews)
    if len(building) == 0:
        data_all.append('None')
    else:
        building_news = building[0].lstrip('建筑结构</span>').rstrip('</li><li><span')
        data_all.append(building_news)

    # 供暖方式
    heating_method = re.findall(u"供暖方式</span>[\u4e00-\u9fa5]+</li><li><span class=.label.>配备电梯", pre_datanews)
    if len(heating_method) == 0:
        data_all.append('None')
    else:
        heating_method_news = heating_method[0].lstrip('供暖方式</span>').rstrip('</li><li><span class="label">配备电梯')
        data_all.append(heating_method_news)

    # 梯户比例
    tihu = re.findall(u"梯户比例</span>[\u4e00-\u9fa5]+</li>", pre_datanews)
    if len(tihu) == 0:
        data_all.append('None')
    else:
        tihu_news = tihu[0].lstrip('梯户比例</span>').rstrip('</li>')
        data_all.append(tihu_news)

    # 产权年限
    chanquan = re.findall(u"产权年限</span>\d+[\u4e00-\u9fa5]</li><li>", pre_datanews)
    if len(chanquan) == 0:
        data_all.append('None')
    else:
        chanquan_news = chanquan[0].lstrip('产权年限</span>').rstrip('</li><li>')
        data_all.append(chanquan_news)

    # 是否配备电梯
    dianti = re.findall(u"配备电梯</span>[\u4e00-\u9fa5]+</li>", pre_datanews)
    if len(dianti) == 0:
        data_all.append('None')
    else:
        dianti_news = dianti[0].lstrip('配备电梯</span>').rstrip('</li>')
        data_all.append(dianti_news)

    # 链家编号
    numberlist = soup.select('.houseRecord')
    numberstr = ''.join([str(i) for i in numberlist])
    number = re.findall(u"链家编号</span><span class=.info.>\d+<span", numberstr)
    if len(number) == 0:
        data_all.append('None')
    else:
        number_news = number[0].lstrip('链家编号</span><span class="info">').rstrip('<span')
        data_all.append(number_news)

    # 交易权属
    quanshu = re.findall(u"交易权属</span>\n<span>[\u4e00-\u9fa5]+</span>", pre_datanews)
    if len(quanshu) == 0:
        data_all.append('None')
    else:
        quanshu_news = quanshu[0].lstrip('交易权属</span>\n<span>').rstrip('</span>')
        data_all.append(quanshu_news)
        # 挂牌时间
    guapai = re.findall(u"挂牌时间</span>\n<span>\d+-\d+-\d+</span>", pre_datanews)
    if len(guapai) == 0:
        data_all.append('None')
    else:
        guapai_news = guapai[0].lstrip('挂牌时间</span>\n<span>').rstrip('</span>')
        data_all.append(guapai_news)

        # 房屋用途
    yongtu = re.findall(u"房屋用途</span>\n<span>[\u4e00-\u9fa5]+</span>", pre_datanews)
    if len(yongtu) == 0:
        data_all.append('None')
    else:
        yongtu_news = yongtu[0].lstrip('房屋用途</span>\n<span>').rstrip('</span>')
        data_all.append(yongtu_news)

    # 房屋年限
    nianxian = re.findall(u"房屋年限</span>\n<span>[\u4e00-\u9fa5]+</span>", pre_datanews)
    if len(nianxian) == 0:
        data_all.append('None')
    else:
        nianxian_news = nianxian[0].lstrip('房屋年限</span>\n<span>').rstrip('</span>')
        data_all.append(nianxian_news)

    # 产权所属
    suoshu = re.findall(u"产权所属</span>\n<span>[\u4e00-\u9fa5]+</span>", pre_datanews)
    if len(suoshu) == 0:
        data_all.append('None')
    else:
        suoshu_news = suoshu[0].lstrip('产权所属</span>\n<span>').rstrip('</span>')
        data_all.append(suoshu_news)

    # 成交额
    data_all.append('None')

    # 挂牌单位价格
    danweiprice = soup.select('.unitPrice')
    if len(danweiprice) == 0:
        data_all.append('None')
    else:
        danweiprice_news = danweiprice[0].text
        data_all.append(danweiprice_news)

    # 上次交易
    jiaoyi = re.findall(u"上次交易</span>\n<span>\d+-\d+-\d+</span>", pre_datanews)
    if len(jiaoyi) == 0:
        data_all.append('None')
    else:
        jiaoyi_news = jiaoyi[0].lstrip('上次交易</span>\n<span>').rstrip('</span>')
        data_all.append(jiaoyi_news)

    # 挂牌价格
    totalprice = soup.select('.total')
    if len(totalprice) == 0:
        data_all.append('None')
    else:
        totalprice_news = totalprice[0].text
        data_all.append(totalprice_news)

    # 成交周期
    data_all.append('None')

    # 调价次数
    data_all.append('None')

    # 本房近30天带看次数
    daikan = soup.select('.totalCount')
    if len(daikan) == 0:
        data_all.append('None')
    else:
        daikan_news = daikan[0].text.lstrip('- 30日带')
        data_all.append(daikan_news)

    # 关注
    guanzhu = soup.select('#favCount')
    if len(guanzhu) == 0:
        data_all.append('None')
    else:
        guanzhu_news = guanzhu[0].text
        data_all.append(guanzhu_news)

    # 浏览次数
    data_all.append('None')

    biaoqian_all = soup.select('div.baseattribute.clear>div.name')
    xiangqing_all = soup.select('div.baseattribute.clear>div.content')
    # 标签1详情1
    if len(biaoqian_all) <= 0:
        data_all.append('None')
    else:
        data_all.append(biaoqian_all[0].text)
    if len(xiangqing_all) <= 0:
        data_all.append('None')
    else:
        data_all.append(xiangqing_all[0].text.lstrip('\n                    ').rstrip('\n                    '))

        # 标签2详情2
    if len(biaoqian_all) <= 1:
        data_all.append('None')
    else:
        data_all.append(biaoqian_all[1].text)
    if len(xiangqing_all) <= 1:
        data_all.append('None')
    else:
        data_all.append(xiangqing_all[1].text.lstrip('\n                    ').rstrip('\n                    '))

        # 标签3详情3
    if len(biaoqian_all) <= 2:
        data_all.append('None')
    else:
        data_all.append(biaoqian_all[2].text)
    if len(xiangqing_all) <= 2:
        data_all.append('None')
    else:
        data_all.append(xiangqing_all[2].text.lstrip('\n                    ').rstrip('\n                    '))

        # 标签4详情4
    if len(biaoqian_all) <= 3:
        data_all.append('None')
    else:
        data_all.append(biaoqian_all[3].text)
    if len(xiangqing_all) <= 3:
        data_all.append('None')
    else:
        data_all.append(xiangqing_all[3].text.lstrip('\n                    ').rstrip('\n                    '))

        # 标签5详情5
    if len(biaoqian_all) <= 4:
        data_all.append('None')
    else:
        data_all.append(biaoqian_all[4].text)
    if len(xiangqing_all) <= 4:
        data_all.append('None')
    else:
        data_all.append(xiangqing_all[4].text.lstrip('\n                    ').rstrip('\n                    '))

        # 标签6详情6
    if len(biaoqian_all) <= 5:
        data_all.append('None')
    else:
        data_all.append(biaoqian_all[5].text)
    if len(xiangqing_all) <= 5:
        data_all.append('None')
    else:
        data_all.append(xiangqing_all[5].text.lstrip('\n                    ').rstrip('\n                    '))
        # 地铁
    dtdata = soup.select('.introContent.showbasemore')
    dtdata_news = ''.join(str(i) for i in dtdata)
    dt = re.findall(u"tag is_near_subway", dtdata_news)
    if len(dt) == 0:
        data_all.append('None')
    else:
        dt_news = '地铁'
        data_all.append(dt_news)

    return data_all


data_pageurls = []
a = []
data_eachurls = []
alldata = []

city_list = get_cityurls(starturl_list[0])
# 得到每页的url
m = 1
for i in city_list:
    try:
        a = get_pageurls(i)
        data_pageurls.extend(a)
        print('得到第{}页网址成功'.format(m))
    except:
        print('得到第{}页网址不成功'.format(m))
    m += 1

# 得到每个房子信息的url
n = 1
for i in data_pageurls:
    try:
        b = get_eachurls(i)
        data_eachurls.extend(b)
        print('得到第{}个房子网址成功'.format(n))
    except:
        print('得到第{}个房子网址不成功'.format(n))
    n += 1

# 得到每个房子信息的url
# n = 1
# for i in data_pageurls:
#    b = get_eachurls(i)
#    data_eachurls.extend(b)
#    print('得到第{}个房子网址成功'.format(n))
#    n +=1

# 得到每户房子信息
r = 1
for i in data_eachurls:
    try:
        c = news_ershoufang(i)
        alldata.append(c)
        print('得到第{}户房子信息成功'.format(r), c[0])
    except:
        print('得到第{}户房子信息不成功'.format(r))
        time.sleep(5)
    r += 1

# 得到每户房子信息
# r = 1
# for i in data_eachurls:
#    c = news_ershoufang(i)
#    alldata.append(c)
#    print('得到第{}户房子信息成功'.format(r))
#    r +=1

df = pd.DataFrame(alldata)
df.columns = ['城市','小区名字','房屋户型','所在楼层','建筑面积','户型结构',\
              '套内面积','建筑类型','房屋朝向','建成年代','装修情况',\
              '建筑结构','供暖方式','梯户比例','产权年限','配备电梯',\
              '链家编号','交易权属','挂牌时间','房屋用途','房屋年限',\
              '产权所属','成交额（万元）','单价（元/平）','上次交易',\
              '挂牌价格','成交周期','调价次数','近30天带看次数','关注人次',\
              '浏览次数','标签1','详情1','标签2','详情2','标签3','详情3','标签4','详情4','标签5','详情5','标签6','详情6','地铁']
df.to_excel('天津.xlsx')
