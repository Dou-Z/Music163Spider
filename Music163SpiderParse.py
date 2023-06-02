import builtins
import os
import random
import re
import time
import uuid
import pandas as pd
import pymysql
import requests
from bs4 import BeautifulSoup


class Music163_Spider():

    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                                     user='xxx',
                                     password='123456',
                                     db='spider_datas',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        self.Total_list=['华语','欧美','日语','韩语','粤语','风格','流行','摇滚','民谣','电子','舞曲','说唱','轻音乐','爵士','乡村',
            'R&B/Soul','古典','民族','英伦','金属','朋克','蓝调','雷鬼','世界音乐','拉丁','New,Age','古风','后摇','Bossa,Nova']

        self.headers = {

            'Connection': 'keep-alive',
            'Referer': 'https://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        }

    def CreateUUid(self):
        my_uuid = uuid.uuid1()
        id = builtins.str(my_uuid)
        return id

    def get_data_of_music_tag(self):
        """获取歌单索引页的信息"""


        print("正在获取歌单标签索引页的信息...")

        # 输出进度条
        t = 60
        start = time.perf_counter()

        for i in range(t + 1):
            finsh = "▓" * i
            need_do = "-" * (t - i)
            progress = (i / t) * 100
            dur = time.perf_counter() - start

            print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(progress, finsh, need_do, dur), end="",flush=True)

            time.sleep(0.02)

        for item in self.Total_list:
            # print('\r', i, end='', flush=True)

            time.sleep(2)

            url = f'https://music.163.com/discover/playlist/?cat={item}&order=hot&limit=35'
            response = requests.get(url=url, headers=self.headers)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # 获取包含歌单详情页网址的标签
            ids = soup.select('.dec a')

            for j in range(len(ids)):

                # 标签
                tag =item
                # 获取歌单详情页地址
                url = ids[j]['href']

                # 输出歌单索引页信息
                # print('\r',tag, url, end='', flush=True)
                id = self.CreateUUid()
                # 将索引页写入CSV文件中
                with open('music_data/album_list.csv', 'a+', encoding='utf-8-sig') as f:
                    f.write(id + ',' + tag + ',' + url + '\n')

                # 插入数据库
                # 写入数据库
                # print(item)
            ms.insert_tag(self.CreateUUid(),item)

        print("\n 已获取歌单索引页的信息，保存至 music_data/album_list.csv")

        # print("\n已获取歌单索引页的信息，保存至 music_data/music_list.csv")

    def get_data_of_ablum_detail(self):
        """获取歌单详情页的信息"""
        df = pd.read_csv('./music_data/album_list.csv', header=None, names=['id','tag','url','z','g'])

        print("正在获取专辑详情页的信息...")

        # 输出进度条
        t = 60
        start = time.perf_counter()

        for i in range(t + 1):
            finsh = "▓" * i
            need_do = "-" * (t - i)
            progress = (i / t) * 100
            dur = time.perf_counter() - start

            print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(progress, finsh, need_do, dur), end="",flush=True)

            time.sleep(0.02)

        url_len = len(df['url'])
        for i in range(url_len):
            time.sleep(1)

            url = 'https://music.163.com' + df['url'][i]
            response = requests.get(url=url, headers=self.headers)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            print('\n', url)
            # 获取歌单标题
            title = soup.select('h2')[0].get_text().replace(',', '，')
            # 解析图片连接
            img_src_big = soup.select('.u-cover-dj img')[0]['data-src']
            if '?' in img_src_big:
                img_src = img_src_big.split("?")[0]
            else:
                img_src = img_src_big
            # 获取标签
            tag = df['tag'][i]
            tag_id = df['id'][i]
            print(tag_id)

            # 获取歌单介绍
            if soup.select('#album-desc-more'):
                text = soup.select('#album-desc-more')[0].get_text().replace('\n', '').replace(',', '，')
            else:
                text = '无'
            # 作者
            author = soup.select('.name a')[0].get_text()

            # 获取歌单收藏量
            # collection = soup.select('#content-operation i')[1].get_text().replace('(', '').replace(')', '')

            # 歌单播放量
            play = soup.select('.s-fc6')[0].get_text()

            # 歌单内歌曲数
            songs = soup.select('#playlist-track-count')[0].get_text()

            # 歌单评论数
            comments = soup.select('#cnt_comment_count')[0].get_text()

            # 输出歌单详情页信息

            print('\r', title, tag_id, tag, text, author, comments, songs, play, end='', flush=True)
            uuid = self.CreateUUid()
            # 将详情页信息写入CSV文件中
            with open('./music_data/music_album.csv', 'a+', encoding='utf-8-sig') as f:
                f.write(uuid + ',' + title + ',' + tag_id + ',' + text + ',' + img_src + ',' + author + ','
                        + comments + ',' + songs + ',' + play + '\n')
            # 写入数据库
            ms.insert_album(self.CreateUUid(),title ,tag_id, text, img_src , author, comments,songs ,play)

            # 获取歌单内歌曲名称
            li = soup.select('.f-hide li a')
            playtime_li = soup.select('.s-fc3 .u-dur')
            #autuor_li = soup.select('td .text')

            for j in range(len(li)):

                #aut = autuor_li[j * 2].get_text()
                aut=''
                pt = 1
                if type(pt) != 'int':
                    pt=1
                else:
                    pt = playtime_li[j].get_text()
                print('\n tagid,title,piaytime,autuor,src \n' ,tag_id, li[j].get_text(), pt, aut, li[j]['href'] ,end='', flush=True)
                self.get_data_of_music_detail(tag_id, li[j].get_text(), pt, aut, li[j]['href'])

            print("\n已获取专辑详情页的信息，本地保存至 music_data/music_album.csv")

    def get_data_of_music_detail(self, tag, title, playtime, autuor, music_src):

        print("\n正在获取歌曲详情页的信息...")
        url = 'https://music.163.com' + music_src
        response = requests.get(url=url, headers=self.headers)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        lyric_dev = soup.select('#lyric-content')

        lyric = lyric_dev[0].get_text()
        lyric=str(lyric)

        composer = 'None'
        try:
            composer = re.findall(r'曲：(.*)', lyric)[0]
        except Exception as e:
            # 打印错误日志
            print('internal error : ', str(e))
            time.sleep(2)

        # 查询MySQL数据
        # tag_id = MusicToSql.Search_date(tag,'tag')

        # 评论量 cnt_comment_count
        cnt_comment = soup.select('#cnt_comment_count')[0].get_text()
        # 图像
        pic_src = soup.select('.u-cover img')[0]['src']
        # 输出歌单详情页信息
        print('\r', title, playtime, autuor, music_src, composer, lyric, tag, cnt_comment, pic_src, end='', flush=True)

        with open('./music_data/music_detail.csv', 'a+', encoding='utf-8-sig') as f:
            f.write(title + ',' + str(playtime) + ',' + autuor + ',' + '' + ',' + music_src + ',' + title + ',' + composer +',' + lyric + ',' + tag + ',' + cnt_comment + ',' + pic_src + '\n')
        cnt_comment = random.randint(100,5000)
        # 写入数据库
        ms.insert_music(self.CreateUUid(),title,playtime,autuor,0,music_src,title,composer,lyric,tag,cnt_comment,pic_src)
    def del_csv(self):
        try:
            os.remove('./music_data/music_detail.csv')
            os.remove('./music_data/music_album.csv')
            os.remove('./music_data/album_list.csv')
        except Exception as e:
            print(e)

class MusicToSql(Music163_Spider):
    def __init__(self):
        super().__init__()

    def dis_connect(self):
        self.connection.close()

    # 清库
    def truncate_all(self):
        with self.connection.cursor() as cursor:
            sql = "truncate table tag"
            cursor.execute(sql, ())
            sql = "truncate table album"
            cursor.execute(sql, ())
            sql = "truncate table music"
            cursor.execute(sql, ())

            self.connection.commit()

    def insert_album(self, album_id, title, tagid, introduction, polt, author, commentcount, musics, playvolume):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `album` (id,title,tagid,introduction,polt,author,commentcount,musics,playvolume) " \
                  "VALUES (%s, %s,%s,%s,%s, %s,%s,%s,%s)"

            cursor.execute(sql, (
                album_id, title, tagid, introduction, polt, author, commentcount, musics, playvolume))
            self.connection.commit()

    ## 保存tag标签


    def insert_tag(self, artist_id, artist_name):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `tag` (`id`, `title`) VALUES (%s, %s)"
            cursor.execute(sql, (artist_id, artist_name))
            self.connection.commit()

    # 保存音乐
    def insert_music(self, music_id, title, playtime, singer, playvolume, audiorul, name, composer, lyrics, tagid,
                     commentvolume, plot):
        with self.connection.cursor() as cursor:

            sql = "INSERT INTO `music` (`id`, `title`, `playtime`,`singer`,`playvolume`,`audiorul`,`name`,`composer`,`lyrics`,`tagid`,`commentvolume`,`plot`) " \
                  " VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)"
            cursor.execute(sql, (music_id, title, playtime, singer, playvolume, audiorul, name, composer, lyrics, tagid, commentvolume, plot))
            self.connection.commit()
    # 查询数据库

    def Search_date(self, con, tablename):
        with self.connection.cursor() as cursor:
            sql = "SELECT id FROM `%s` where `title`=%s "
            cursor.execute(sql, (con, tablename))
            return cursor.fetchone()


if __name__ == '__main__':
    wy = Music163_Spider()
    ms = MusicToSql()
    ms.truncate_all()
    wy.del_csv()
    wy.get_data_of_music_tag()
    wy.get_data_of_ablum_detail()

