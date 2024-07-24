import os
import re
import configparser
import pypinyin
from plexapi.server import PlexServer
from pykakasi import kakasi

# 获取脚本当前所在文件夹
script_dir = os.path.dirname(__file__)
dict_list = os.path.join(script_dir,'config.ini')

# 从config.ini获取对应字典
config = configparser.ConfigParser()
config.read(dict_list, encoding='utf-8')
tags = dict(config.items('Genres'))
country = dict(config.items('Countries'))
editions = dict(config.items('Editions'))

def plex_server():
    # 获取PLEX配置
    plex_server = dict(config.items('Server'))
    PLEX_URL = plex_server['plex_url']
    PLEX_TOKEN = plex_server['plex_token']
    
    # 连接PLEX服务器
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    return plex

# 检查是否包含英文
def check_contain_english(check_str):
    return bool(re.search('[a-z]', check_str))

# 检查是否包含中文
def check_contain_chinese(check_str):
     for str in check_str:
         if '\u4e00' <= str <= '\u9fff':
             return True
     return False
 
# 中文转换拼音
def chinese_to_pinyin(chinese):
    pinyin_list = pypinyin.lazy_pinyin(chinese)
    pinyin = ''.join(pinyin_list).title()
    
    # 处理特殊字符
    pattern = re.compile(u"[^a-zA-Z0-9]")
    pinyin = re.sub(pattern, ' ', pinyin)
    return pinyin

# 中文转换拼音首字母拼接
def chinese_to_pinyin_first_letter(chinese):
    str_list = []
    pinyin_list = pypinyin.pinyin(chinese, style=pypinyin.FIRST_LETTER, heteronym=True)
    for i in range(len(pinyin_list)):
        str_list.append(str(pinyin_list[i][0]).upper())
    pinyin_first_letter = ''.join(str_list)
    
    # 处理特殊字符
    pattern = re.compile(u"[^a-zA-Z0-9]")
    pinyin_first_letter = re.sub(pattern, ' ', pinyin_first_letter)
    return pinyin_first_letter

# 检查是否包含日文
def check_contain_japanese(check_str):
    pattern = re.compile(r'[\u3040-\u30FF\u31F0-\u31FF\uFF65-\uFF9F]+')
    for str in check_str:
        match = pattern.search(str)
        if match:
            return True
    return False

# 日文转换罗马音
def japanese_to_romaji(japanese):
    japanese_dict = kakasi().convert(japanese)
    romaji = ' '.join([word['hepburn'] for word in japanese_dict])
    return romaji

# 日文转换平假名
def japanese_to_hirakana(japanese):
    japanese_dict = kakasi().convert(japanese)
    hirakana = ' '.join([word['hira'] for word in japanese_dict])
    return hirakana

# 日文转换片假名
def japanese_to_katakana(japanese):
    japanese_dict = kakasi().convert(japanese)
    katakana = ' '.join([word['kana'] for word in japanese_dict])
    return katakana


# 更新类别
def updategenres(item, genres):
    ch_list=[]
    eng_list=[]
    for genre in genres:
        try:
            genre = genre.tag
        except:
            pass
        if genre.lower() in tags.keys():
            zh = tags[genre.lower()]
            ch_list.append(zh)
            eng_list.append(genre)
    if len(eng_list) > 0: 
        item.addGenre(ch_list, locked=False)
        item.removeGenre(eng_list, locked=True)

# 更新国家
def updatecountries(item, countries):
    en_list=[]
    ch_list=[]
    for c in countries:
        try:
            c = c.tag
        except:
            pass
        if c.lower() in country.keys():
            zh = country[c.lower()]
            ch_list.append(zh)
            en_list.append(c)
    if len(en_list) > 0: 
        item.addCountry(ch_list, locked=False)
        item.removeCountry(en_list, locked=True)

# 更新季度信息
def update_season(season):
    season_title = season.title
    season_no = season.index
    season_ends = season_title[1:]
    season_starts = season_title[:-1]
    # 纯英文季度名
    if check_contain_chinese(season_title) == False:
        if len(str(season_no)) >= 4:
            season.editTitle(f'{season_no} 年', True)
        else:
            season.editTitle(f'第 {season_no} 季', True)
    # 第 0 季统称特别篇
    elif season_no == 0 and season_title != '特别篇':
        season.editTitle('特别篇', True)
    # 以季开头,纯数字结尾的
    elif season_title.startswith('季'):
        if season_ends.isdigit():
            # 四位数季度改为年份
            if len(season_ends) >= 4:
                season.editTitle(f'{season_no} 年', True)
            else:
                season.editTitle(f'第 {season_no} 季', True)
    # 第1季统一改成第 1 季 / 1999年改成1999年 (暂未考虑其他)
    elif season_title.startswith('第') and season_title.endswith('季'):
        if season_title != f'第 {season_no} 季':
            season.editTitle(f'第 {season_no} 季', True)
    elif season_title.endswith('年') and season_starts.isdigit():
        if season_title != f'{season_no} 年':
            season.editTitle(f'{season_no} 年', True)