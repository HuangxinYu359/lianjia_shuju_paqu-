#导包
from bs4 import BeautifulSoup
import requests
import re
import time
import pandas as pd
import json
import time

#伪造设置浏览器请求头user-agent
#修改starturl_list即可
head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
starturl_list = ['https://cs.lianjia.com/chengjiao/']

#获取县级市的url
def get_cityurls(url):
    request = requests.get(url,headers=head)
    request.encoding = 'utf-8'
    soup = BeautifulSoup(request.text,'html.parser')
    cityurls = []
    prenews = soup.select('div.position>dl>dd>div>div>a')
    pre_news =  ''.join([str(i) for i in prenews])
    nameslist = re.findall("/chengjiao/[a-zA-Z0-9]+/. t",pre_news)
    namesliststrip = [i.lstrip('/chengjiao/').rstrip('" t')  for i in nameslist]
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
    data_all.append('长沙')

    # 小区名字
    names = soup.select('div.house-title>div.wrapper')
    names_pre = ''.join(str(i) for i in names)
    names_predata = re.findall("^<div class=.wrapper.>[\u4e00-\u9fa5]+ ", names_pre)
    if len(names) == 0:
        data_all.append('None')
    else:
        names_news = names_predata[0].lstrip('<div class="wrapper">').rstrip(' ')
        data_all.append(names_news)

    # 室厅厨卫
    shi = re.findall(u"房屋户型</span>[\d\u4e00-\u9fa5]+", pre_datanews)
    if len(shi) == 0:
        data_all.append('None')
    else:
        shi_news = shi[0].lstrip('房屋户型</span>')
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
    huxing = re.findall(u"户型结构</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(huxing) == 0:
        data_all.append('None')
    else:
        huxing_news = huxing[0].lstrip('户型结构</span>')
        data_all.append(huxing_news)

    # 套内面积
    home_area = re.findall(
        u"套内面积</span>.+<li><span class=.label.>建筑类型|套内面积</span>[\u4e00-\u9fa5]+<li><span class=.label.>建筑类型",
        pre_datanews)
    if len(home_area) == 0:
        data_all.append('None')
    else:
        home_areanews = home_area[0].lstrip('套内面积</span>').rstrip('<li><span class="label">建筑类型').rstrip('      </')
        data_all.append(home_areanews)

    # 建筑类型
    label = re.findall(u"建筑类型</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(label) == 0:
        data_all.append('None')
    else:
        label_news = label[0].lstrip('建筑类型</span>')
        data_all.append(label_news)

    # 房屋朝向
    if len(pre_data) < 7:
        data_all.append('None')
    else:
        direction_news = pre_data[6].text.lstrip('房屋朝向')
        data_all.append(direction_news)

    # 建成年代
    com_time = re.findall(u"建成年代</span>\d+", pre_datanews)
    if len(com_time) == 0:
        data_all.append('None')
    else:
        com_timenews = com_time[0].lstrip('建成年代</span>')
        data_all.append(com_timenews)

    # 装修情况
    fitment = re.findall(u"装修情况</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(fitment) == 0:
        data_all.append('None')
    else:
        fitment_news = fitment[0].lstrip('装修情况</span>')
        data_all.append(fitment_news)

    # 建筑结构
    building = re.findall(u"建筑结构</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(building) == 0:
        data_all.append('None')
    else:
        building_news = building[0].lstrip('建筑结构</span>')
        data_all.append(building_news)

    # 供暖方式
    heating_method = re.findall(u"供暖方式</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(heating_method) == 0:
        data_all.append('None')
    else:
        heating_method_news = heating_method[0].lstrip('供暖方式</span>')
        data_all.append(heating_method_news)

    # 梯户比例
    tihu = re.findall(u"梯户比例</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(tihu) == 0:
        data_all.append('None')
    else:
        tihu_news = tihu[0].lstrip('梯户比例</span>')
        data_all.append(tihu_news)

    # 产权年限
    chanquan = re.findall(u"产权年限</span>\d+[\u4e00-\u9fa5]", pre_datanews)
    if len(chanquan) == 0:
        data_all.append('None')
    else:
        chanquan_news = chanquan[0].lstrip('产权年限</span>')
        data_all.append(chanquan_news)

    # 是否配备电梯
    dianti = re.findall(u"配备电梯</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(dianti) == 0:
        data_all.append('None')
    else:
        dianti_news = dianti[0].lstrip('配备电梯</span>')
        data_all.append(dianti_news)

    # 链家编号
    numberlist = re.findall(u"链家编号</span>\d+", pre_datanews)
    if len(numberlist) == 0:
        data_all.append('None')
    else:
        numberlist_news = numberlist[0].lstrip('链家编号</span>')
        data_all.append(numberlist_news)

    # 交易权属
    quanshu = re.findall(u"交易权属</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(quanshu) == 0:
        data_all.append('None')
    else:
        quanshu_news = quanshu[0].lstrip('交易权属</span>\n<span>')
        data_all.append(quanshu_news)

        # 挂牌时间
    guapai = re.findall(u"挂牌时间</span>\d+-\d+-\d+|挂牌时间</span>\d+-\d+", pre_datanews)
    if len(guapai) == 0:
        data_all.append('None')
    else:
        guapai_news = guapai[0].lstrip('挂牌时间</span>\n<span>')
        data_all.append(guapai_news)

        # 房屋用途
    yongtu = re.findall(u"房屋用途</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(yongtu) == 0:
        data_all.append('None')
    else:
        yongtu_news = yongtu[0].lstrip('房屋用途</span>')
        data_all.append(yongtu_news)

    # 房屋年限
    nianxian = re.findall(u"房屋年限</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(nianxian) == 0:
        data_all.append('None')
    else:
        nianxian_news = nianxian[0].lstrip('房屋年限</span>')
        data_all.append(nianxian_news)

    # 产权所属
    suoshu = re.findall(u"房权所属</span>[\u4e00-\u9fa5]+", pre_datanews)
    if len(suoshu) == 0:
        data_all.append('None')
    else:
        suoshu_news = suoshu[0].lstrip('房权所属</span>')
        data_all.append(suoshu_news)

    jiaoyi = soup.select('div.price')
    jiaoyi_news = jiaoyi[0].text

    # 成交额
    chengjiaoprice = re.findall(u"\d+万", jiaoyi_news)
    if len(chengjiaoprice) == 0:
        data_all.append('None')
    else:
        chengjiaoprice_news = chengjiaoprice[0]
        data_all.append(chengjiaoprice_news)

    # 成交单位价格
    danweiprice = re.findall(u"\d+元/平|\d+元\平", jiaoyi_news)
    if len(danweiprice) == 0:
        data_all.append('None')
    else:
        danweiprice_news = danweiprice[0]
        data_all.append(danweiprice_news)

    # 成交日期
    cjtime = re.findall("\d+.\d+.\d+ +成交", names_pre)
    if len(cjtime) == 0:
        data_all.append('None')
    else:
        cjtime_news = cjtime[0].rstrip('成交')
        data_all.append(cjtime_news)

    dataformsg = soup.select('div.msg')
    dataformsg_news = ''.join(str(i) for i in dataformsg)
    # 挂牌价格
    guapaiprice = re.findall("\d+</label>挂牌价格", dataformsg_news)
    if len(guapaiprice) == 0:
        data_all.append('None')
    else:
        guapaiprice_news = guapaiprice[0].rstrip('</label>挂牌价格')
        data_all.append(guapaiprice_news)

    # 成交周期
    cjzq = re.findall("\d+</label>成交周期", dataformsg_news)
    if len(cjzq) == 0:
        data_all.append('None')
    else:
        cjzq_news = cjzq[0].rstrip('</label>成交周期')
        data_all.append(cjzq_news)

    # 调价次数
    adjust = re.findall("\d+</label>调价", dataformsg_news)
    if len(adjust) == 0:
        data_all.append('None')
    else:
        adjust_news = adjust[0].rstrip('</label>调价')
        data_all.append(adjust_news)

    # 带看次数
    daikan = re.findall("\d+</label>带看", dataformsg_news)
    if len(daikan) == 0:
        data_all.append('None')
    else:
        daikan_news = daikan[0].rstrip('</label>带看')
        data_all.append(daikan_news)

    # 关注
    guanzhu = re.findall("\d+</label>关注", dataformsg_news)
    if len(guanzhu) == 0:
        data_all.append('None')
    else:
        guanzhu_news = guanzhu[0].rstrip('</label>关注')
        data_all.append(guanzhu_news)

    # 浏览次数
    liulan = re.findall("\d+</label>浏览", dataformsg_news)
    if len(liulan) == 0:
        data_all.append('None')
    else:
        liulan_news = liulan[0].rstrip('</label>浏览')
        data_all.append(liulan_news)

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
    dt = re.findall(u">地铁</a>", dtdata_news)
    if len(dt) == 0:
        data_all.append('None')
    else:
        dt_news = dt[0].lstrip('>').rstrip('</a>')
        data_all.append(dt_news)
    return data_all

#% %time
data_pageurls = []
a = []
data_eachurls = []
alldata = []


city_list = get_cityurls(starturl_list[0])
#得到每页的url
m = 1
for i in city_list:
    try:
        a = get_pageurls(i)
        data_pageurls.extend(a)
        print('得到第{}页网址成功'.format(m))
    except:
        print('得到第{}页网址不成功'.format(m))
    m +=1

#得到每个房子信息的url
n = 1
for i in data_pageurls:
    try:
        b = get_eachurls(i)
        data_eachurls.extend(b)
        print('得到第{}个房子网址成功'.format(n))
    except:
        print('得到第{}个房子网址不成功'.format(n))
    n +=1

#得到每户房子信息
r = 1
for i in data_eachurls:
    try:
        c = news_ershoufang(i)
        alldata.append(c)
        print('得到第{}户房子信息成功'.format(r),c[0])
    except:
        print('得到第{}户房子信息不成功'.format(r))
        time.sleep(5)
    r +=1

df = pd.DataFrame(alldata)
df.columns = ['城市','小区名字','房屋户型','所在楼层','建筑面积','户型结构',\
              '套内面积','建筑类型','房屋朝向','建成年代','装修情况',\
              '建筑结构','供暖方式','梯户比例','产权年限','配备电梯',\
              '链家编号','交易权属','挂牌时间','房屋用途','房屋年限',\
              '产权所属','成交额（万元）','单价（元/平）','上次交易',\
              '挂牌价格','成交周期','调价次数','近30天带看次数','关注人次',\
              '浏览次数','标签1','详情1','标签2','详情2','标签3','详情3','标签4','详情4','标签5','详情5','标签6','详情6','地铁']
df.to_excel('长沙.xlsx')