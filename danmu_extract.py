import requests,re,time
from pprint import pprint
from xml.etree import ElementTree as ET
from xml.dom import minidom
from scrapy.selector import Selector


class BilibiliDanmu:

    def __init__(self):
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://message.bilibili.com',
            'Referer': 'https://message.bilibili.com/pages/nav/index_new_sync',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
            }

    def ani_parse(self):
        ep_url = self.av_id_or_url
        res = requests.get(ep_url, headers=self.headers)
        sel = Selector(text=res.text)
        self.author = ""
        self.title = sel.xpath("//div[@class='media-wrapper']/h1/@title").extract_first()
        self.av_id = sel.xpath("//a[@class='av-link']/text()").extract_first()
        pattern = re.compile('''.*?"epInfo".+?"cid":(\d+)''', flags=re.DOTALL)
        cid_num = pattern.search(res.text).group(1)
        return cid_num

    def vd_parse(self):
        av_url = 'https://www.bilibili.com/video/{}'.format(self.av_id_or_url) if self.av_id_or_url.startswith(
            'av') else self.av_id_or_url
        self.av_id = re.search('av\d+', av_url).group(0)
        res = requests.get(av_url,headers=self.headers)
        sel = Selector(text=res.text)
        title_and_type = sel.xpath("//meta[@itemprop='keywords']/@content").extract_first()
        title_and_type = title_and_type.split(",")
        self.title = title_and_type[0]
        self.av_type = ','.join(title_and_type[1:-4])
        self.author = sel.xpath("//meta[@itemprop='author']/@content").extract_first()
        self.pub_time = sel.xpath("//meta[@itemprop='datePublished']/@content").extract_first()
        pattern = re.compile('''.*?"cid":(\d+)''', flags=re.DOTALL)
        cid_num = pattern.search(res.text).group(1)
        return cid_num


    def parse_danmu(self,cid):
        danmu_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=%s' % cid
        res = requests.get(danmu_url)
        res.encoding = "utf-8"
        # 从xml中提取弹幕数据
        xml_string = minidom.parseString(res.text)
        for node in xml_string.getElementsByTagName("d"):
            text = node.childNodes[0].nodeValue
            time_list = node.getAttribute("p").split(",")
            av_sec = int(float(time_list[0]))
            m,s = divmod(av_sec,60)
            video_time = '%02d分%02d秒' % (m,s)
            timeArray = time.localtime(int(time_list[4]))
            com_time = time.strftime("%Y/%m/%d %H:%M:%S", timeArray)
            yield video_time,text,com_time
        # print(node,node.getAttribute("p"),text_node.nodeValue)


    def save_txt(self):
        while(True):
            self.av_id_or_url = input('请输入视频av号或视频链接：')
            if self.av_id_or_url == '退出':
                break
            else:
                try:
                    self.av_id_or_url.index('bangumi')
                    cid = self.ani_parse()
                except:
                    cid = self.vd_parse()

            f = open("%s.txt" % (self.av_id), "w", encoding='utf-8')
            f.write("视频标题：{}\n".format(self.title))
            if self.author:
                f.write("视频类型：{}\n".format(self.av_type))
                f.write("视频作者：{}\n".format(self.author))
                f.write("发布时间：{}\n".format(self.pub_time))
            f.write("视频编号：{}\n\n".format(self.av_id))
            content_list = self.parse_danmu(cid)
            for each in content_list:
                video_time = each[0]
                text = each[1]
                com_time = each[2]
                f.write("{0}\t\t{2}\t{1}\n".format(video_time, text, com_time))
            f.close()


if __name__ == "__main__":
    danmu = BilibiliDanmu()
    danmu.save_txt()




    
    
                    
            

                
                    


        
