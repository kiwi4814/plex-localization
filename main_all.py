#### 更新全部 把main.py里面的check_contain_chinese后面的sort去掉，全部（21个）
#### 修改内容：reload增加retry，三次后跳过；不对音频做处理
# 导入模块
import datetime
from components.function import *
from components.log import *
from zhconv import convert
import jieba
import time

def reload_item_with_timeout(item, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            item.reload()
            # 如果成功重新加载，退出函数
            return True
        except Exception as e:  # 根据实际情况替换为你得到的超时异常类型
            print(f"项目 '{item.title}' 连接超时，等待30秒后重试...")
            time.sleep(30)
            retries += 1

    # 在超过最大重试次数后记录错误日志并返回False
    print(f"项目 '{item.title}' 重试了{max_retries}次后仍然失败。跳过此项目。")
    logger.error(f"项目 '{item.title}' 重试了{max_retries}次后仍然失败。跳过此项目。") # 如果有logger，取消注释这行
    return False

def loopThroughAllItems(plex, logger, day, section):
    # 设定更新x天内有过更新元数据的电影/电视剧/剧集
    olddate = datetime.datetime.now().date() - datetime.timedelta(days = day-1)

    # 如果库是电影或者剧集类型
    if section.type in ('movie','show'):
        
        # 获取库内所有的项目(项目指整部电影/整部剧集)
        for item in section.all():
            # try:
            #     # 获取项目更新元数据的时间
            #     updated_date = datetime.datetime.date(item.updatedAt)
            # except item.updatedAt == 'none':
            #     # 部分项目无更新时间时则按当天作为更新时间
            #     updated_date = olddate + datetime.timedelta(days = 0)
            try:
                # 获取项目更新元数据的时间
                updated_date = item.updatedAt.date()
            except AttributeError:
                # 部分项目无更新时间时则按当天作为更新时间
                updated_date = datetime.datetime.now().date()
            
            # 如项目更新时间大于设定的x天时间
            if updated_date >= olddate:
                # 重载项目 (未重载时项目的类别/国家数据不齐全)
                # item.reload()
                # 重载项目并检查是否成功
                if not reload_item_with_timeout(item):
                    # 如果重载失败，跳过此项目
                    continue
                # 只包含大写字母
                if item.titleSort.isupper():
                    pinyin = chinese_to_pinyin(item.title)
                    first_letter = chinese_to_pinyin_first_letter(item.title)
                    split_words = " ".join(jieba.cut(item.title, cut_all=True))
                    word_pinyin = chinese_to_pinyin(split_words)
                    word_first_letter = chinese_to_pinyin_first_letter(split_words)
                    title = pinyin + " " + first_letter + " " + word_pinyin + " " + word_first_letter
                    item.editSortTitle(title, True)
                    logger.info(f'{section.title} {section.type.capitalize()} - {item.title}, 更新标题')
                    print(f'{section.title} {section.type.capitalize()} - {item.title}, 更新标题')
                # 如项目标题包含中文则用拼音首字母拼接后更新标题
                if check_contain_chinese(item.titleSort):
                    pinyin = chinese_to_pinyin(item.title)
                    first_letter = chinese_to_pinyin_first_letter(item.title)
                    split_words = " ".join(jieba.cut(item.title, cut_all=True))
                    word_pinyin = chinese_to_pinyin(split_words)
                    word_first_letter = chinese_to_pinyin_first_letter(split_words)
                    title = pinyin + " " + first_letter + " " + word_pinyin + " " + word_first_letter
                    item.editSortTitle(title, True)
                    logger.info(f'{section.title} {section.type.capitalize()} - {item.title}, 更新标题')
                    print(f'{section.title} {section.type.capitalize()} - {item.title}, 更新标题')

                # 如项目类别包含英文则更新类别为中文
                if item.genres:
                    genres = item.genres
                    for genre in genres:
                        if check_contain_english(genre.tag):
                            updategenres(item, genres)
                            logger.info(f'{section.title} {section.type.capitalize()} - {item.title} 更新类别')
                            print(f'{section.title} {section.type.capitalize()} - {item.title} 更新类别')
                            break     

                # 如电影的国家包含英文则更新国家为中文(剧集不支持)                 
                if section.type == 'movie':
                    if item.countries:
                        countries = item.countries
                        for country in countries:
                            if check_contain_english(country.tag):
                                updatecountries(item, countries)
                                logger.info(f'{section.title} {section.type.capitalize()} - {item.title} 更新国家')
                                print(f'{section.title} {section.type.capitalize()} - {item.title} 更新国家')
                                break

                    # 如电影的版本(edition)包含英文则更新为中文(剧集不支持)
                    if item.editionTitle:
                        edition = item.editionTitle
                        edition = edition.lower()
                        if edition in editions.keys():
                            item.editEditionTitle(editions[edition], True)
                            logger.info(f'{section.title} {section.type.capitalize()} - {item.title} 更新版本')
                            print(f'{section.title} {section.type.capitalize()} - {item.title} 更新版本')

                # 更新季度标题
                if section.type == 'show':
                    for season in item.seasons():
                        update_season(season)
                    # 如剧集里面的单集标题包含中文则用拼音首字母拼接后更新标题
                    for episode in item.episodes():
                        if check_contain_chinese(episode.title):
                            pinyin = chinese_to_pinyin(episode.title)
                            first_letter = chinese_to_pinyin_first_letter(episode.title)
                            split_words = " ".join(jieba.cut(episode.title, cut_all=True))
                            word_pinyin = chinese_to_pinyin(split_words)
                            word_first_letter = chinese_to_pinyin_first_letter(split_words)
                            title = pinyin + " " + first_letter + " " + word_pinyin + " " + word_first_letter
                            episode.editSortTitle(title, True)
                            logger.info(f'{section.title} {section.type.capitalize()} - {item.title} - {episode.title} 更新标题')
                            print(f'{section.title} {section.type.capitalize()} - {item.title} - {episode.title} 更新标题')

        # 获取电影库的所有电影合集
        for collection in section.collections():     
            # 如电影合集内容不为空且合集标题包含中文时用拼音首字母拼接后更新电影合集标题                 
            if collection.content == None and check_contain_chinese(collection.title):
                pinyin = chinese_to_pinyin(collection.title)
                first_letter = chinese_to_pinyin_first_letter(collection.title)
                split_words = " ".join(jieba.cut(collection.title, cut_all=True))
                word_pinyin = chinese_to_pinyin(split_words)
                word_first_letter = chinese_to_pinyin_first_letter(split_words)
                title = pinyin + " " + first_letter + " " + word_pinyin + " " + word_first_letter
                collection.editSortTitle(title, True)
                logger.info(f'{section.title} Collection - {collection.title} 更新合集标题')
                print(f'{section.title} Collection - {collection.title} 更新合集标题')
                
    # 如果库是音乐类型
    # if section.type == 'artist':
        
    #     # 获取音乐库的所有艺术家
    #     for artist in section.all():
    #         try:
    #             # 获取项目更新元数据的时间
    #             updated_date = datetime.datetime.date(artist.updatedAt)
    #         except artist.updatedAt == 'none':
    #             # 部分项目无更新时间时则按当天作为更新时间
    #             updated_date = olddate + datetime.timedelta(days = 0)
            
    #         # 如项目更新时间大于设定的x天时间
    #         if updated_date >= olddate:
            
    #             # 如艺术家的国家包含英文则更新国家为中文
    #             if artist.countries:
    #                 countries = artist.countries
    #                 for country in countries:
    #                     if check_contain_english(country.tag):
    #                         updatecountries(artist, countries)
    #                         logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 更新国家')
    #                         print(f'{section.title} {section.type.capitalize()} - {artist.title} 更新国家')
    #                         break
                
    #             # 艺术家名称索引优化
    #             if artist.countries and artist.countries[0].tag in ("日本", "Japan"):
                    
    #                 # 日本 优化艺术家名称索引
    #                 if check_contain_japanese(artist.title):                 
    #                     sortTitle = japanese_to_romaji(artist.title) + " " + japanese_to_hirakana(artist.title) + " " + japanese_to_katakana(artist.title)
    #                     artist.editSortTitle(sortTitle, True)
    #                     logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 优化索引')
    #                     print(f'{section.title} {section.type.capitalize()} - {artist.title} 优化索引')
    #                 else:
    #                     if check_contain_chinese(artist.title):
    #                         if check_contain_chinese(artist.title):
    #                             # 艺术家名称繁体转简体
    #                             title = convert(artist.title, 'zh-cn')
    #                             artist.editTitle(title, True)
    #                             logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 繁体转简体')
    #                             print(f'{section.title} {section.type.capitalize()} - {artist.title} 繁体转简体')
                            
    #                             # 优化艺术家名称索引
    #                             title = chinese_to_pinyin(artist.title) + " " + chinese_to_pinyin_first_letter(artist.title)
    #                             artist.editSortTitle(title, True)
    #                             logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 添加拼音及首字母索引')
    #                             print(f'{section.title} {section.type.capitalize()} - {artist.title} 添加拼音及首字母索引')
    #             else:
                    
    #                 if check_contain_chinese(artist.title):
    #                     if check_contain_chinese(artist.title):
    #                         # 艺术家名称繁体转简体
    #                         title = convert(artist.title, 'zh-cn')
    #                         artist.editTitle(title, True)
    #                         logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 繁体转简体')
    #                         print(f'{section.title} {section.type.capitalize()} - {artist.title} 繁体转简体')
                        
    #                         # 优化艺术家名称索引
    #                         title = chinese_to_pinyin(artist.title) + " " + chinese_to_pinyin_first_letter(artist.title)
    #                         artist.editSortTitle(title, True)
    #                         logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 添加拼音及首字母索引')
    #                         print(f'{section.title} {section.type.capitalize()} - {artist.title} 添加拼音及首字母索引')
                        
    #             # 优化专辑索引
    #             for album in artist.albums():
                    
    #                 if artist.countries and artist.countries[0].tag in ("日本", "Japan") or artist.title == 'Various Artists':
                        
    #                     if check_contain_japanese(album.title):                 
    #                         sortTitle = japanese_to_romaji(album.title) + " " + japanese_to_hirakana(album.title) + " " + japanese_to_katakana(album.title)
    #                         album.editSortTitle(sortTitle, True)
    #                         logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title}优化索引')
    #                         print(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 优化索引')
                            
    #                     else:
                            
    #                         if check_contain_chinese(album.title):
    #                             if check_contain_chinese(album.title):
    #                                 # 专辑名称繁体转简体
    #                                 title = convert(album.title, 'zh-cn')
    #                                 album.editTitle(title, True)
    #                                 logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 繁体转简体')
    #                                 print(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 繁体转简体')
                                
    #                                 # 优化专辑名称索引
    #                                 title = chinese_to_pinyin(album.title) + " " + chinese_to_pinyin_first_letter(album.title)
    #                                 album.editSortTitle(title, True)
    #                                 logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 添加拼音及首字母索引')
    #                                 print(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 添加拼音及首字母索引')
    #                 else:
                        
    #                     if check_contain_chinese(album.title):
    #                         if check_contain_chinese(album.title):
    #                             # 专辑名称繁体转简体
    #                             title = convert(album.title, 'zh-cn')
    #                             album.editTitle(title, True)
    #                             logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} 繁体转简体')
    #                             print(f'{section.title} {section.type.capitalize()} - {artist.title} 繁体转简体')
                            
    #                             # 优化专辑名称索引
    #                             title = chinese_to_pinyin(album.title) + " " + chinese_to_pinyin_first_letter(album.title)
    #                             album.editSortTitle(title, True)
    #                             logger.info(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 添加拼音及首字母索引')
    #                             print(f'{section.title} {section.type.capitalize()} - {artist.title} {album.title} 添加拼音及首字母索引')

    print(f"{section.title} 完成处理!")

if __name__ == "__main__":

    # 连接PLEX服务器
    plex = plex_server()

    # 开启日志
    logger = get_logger()
    
    # 手动指定媒体库功能；True为开启，False为关闭
    section_range = False

    # 手动指定日期范围功能；True为开启，False为关闭
    date_range = False
        
    # 默认更新日期范围; 1代表24小时内有更新的媒体；2代表48小时
    if date_range == False:
        day = 9999
        logger.info(f"更新{day}天内有过更新/加入的媒体")
        print(f"更新{day}天内有过更新/加入的媒体")
    
    # 确定更新的日期范围 (x天内更新过元数据)
    while date_range:
        day = input('仅更新今天加入的吗?\n如是请按回车, 如不是请回复数字\n退出请回复Q: ')
        if day == '':
            day = 1
            break
        elif day.upper() == 'Q':
            exit()
        else:
            try:
                day = int(day)
                break
            except ValueError:
                print('\n输入错误, 请输入阿拉伯数字的整数\n')
                
    # 更新指定媒体库功能
    if section_range == False:
        # 默认更新全部媒体库
        sections = 'all'
    else:
        # 获取服务器的媒体库列表
        section_list = []    
        for section in plex.library.sections():
            print(f'{section.key} - {section.type} - {section.title}')
            section_list.append(section.key)
    
    # 确定更新哪几个媒体库或全部媒体库
    while section_range:
        sections = input('请输入媒体库ID数字\n多个以逗号分隔, 不回复按回车则更新全部媒体库, 退出请回复Q: ')
        if sections == '':
            sections = 'all'
            break
        elif sections.upper() == 'Q':
            exit()
        elif ',' in sections or '，' in sections:
            sections = sections.replace('，',',').split(sections,',')
            for sectionId in sections:
                try:
                    if int(sectionId) not in section_list:
                        print('\n输入错误, 请输入媒体库对应的数字\n')
                        break
                except ValueError:
                    print('\n输入错误, 请输入阿拉伯数字的整数\n')
                    break
            else:
                break
        else:
            try:
                sections = int(sections)
                if sections not in section_list:
                    print('\n输入错误, 请输入媒体库对应的数字\n')
                else:
                    break
            except ValueError:
                print('\n输入错误, 请输入阿拉伯数字的整数\n')
                
    # 如更新多个媒体库
    if type(sections) == list:
        for section in sections:
            section = plex.library.sectionByID(int(section))
            loopThroughAllItems(plex, logger, int(day), section)
    # 如更新全部媒体库
    elif sections == 'all':
        sections = plex.library.sections()
        for section in sections:
            loopThroughAllItems(plex, logger, int(day), section)
    # 如更新单个媒体库
    else:
        section = plex.library.sectionByID(sections)
        loopThroughAllItems(plex, logger, int(day), section)