# coding=utf-8
'''
process.py：数据处理
'''

import jieba
import numpy as np
from wordcloud import ImageColorGenerator, WordCloud
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.font_manager as fm
import PIL.Image as Image
import pandas as pd


pathList = ['202001', '202002', '202003']
days = [31, 29, 31]

firstPageTitles = ''
allTitles = []
wordCntDictList = []
totalPages = []
impPages = []
firstPages = []


# 读取存储的数据
def Readin():
    global firstPageTitles

    # 对每月（每个文件夹）
    for i in range(3):
        # 获取统计数据并存入列表
        stats = np.loadtxt('./file/{}/stats.txt'.format(pathList[i]), dtype=np.int)
        totalPages.extend(stats[:,0].T.tolist())
        impPages.extend(stats[:,1].T.tolist())
        firstPages.extend(stats[:,2].T.tolist())

        titles = ''
        for j in range(1, days[i]+1):
            # 逐行读取当天标题
            cnt = 0
            with open('./file/{}/{:0>2d}.txt'.format(pathList[i], j), 'r', encoding='utf-8') as f:
                line = f.readline()
                while line:
                    cnt += 1
                    # 头版文章
                    if cnt <= stats[j-1][2]:
                        firstPageTitles += line
                    titles += line
                    line = f.readline()
            # 一旬结束，将当旬标题总字符串存入列表
            if j == 10 or j == 20:
                allTitles.append(titles)
                titles = ''
        # 最后一旬的标题总字符串
        allTitles.append(titles)


# 页数折线图
def DrawPagesCount():
    myfont = fm.FontProperties(fname = r'msyh.ttc')

    x = np.arange(3, 94, 1)
    y_t = np.array(totalPages, dtype = np.int)
    y_p = np.array(impPages)
    xticks = [i for i in range(1, 96, 7)]

    axt = plt.subplot(1, 1, 1, facecolor='white')

    axt.set_xlim(0, 96)
    axt.set_ylim(0, 25)
    xmajorLocator = MultipleLocator(7)
    ymajorLocator = MultipleLocator(5)
    axt.xaxis.set_major_locator(xmajorLocator)
    axt.xaxis.set_major_locator(ymajorLocator)
    axt.xaxis.grid(True, which='major')
    axt.yaxis.grid(True, which='major')
    axt.set_xticks(xticks)
    plott = axt.plot(x, y_t, alpha = 0.5, color='r', label = '总页数')
    plotp = axt.plot(x, y_p, alpha = 0.5, color='b', label = '要闻页数')
    axt.legend(prop = myfont)
    plt.savefig('Pages.jpg', dpi=400)
    plt.show()


# 停用词：标点符号
stopwords1 = ['\n', '\r\n', '，', '（', '）', '—', ' ', '——', '《', '》',
                '“', '”', '‘', '’', '(', ')', '；', '、', '·']
# 停用词：常见人名、职称、人称代词等
stopwords2 = ['习近平', '主席','总书记', '李克强', '总理', '我们', '强调']


# 字符串分词
def CutWords(string):
    wordList = [x for x in jieba.cut(string) if x not in stopwords1]
    return wordList


# 创建词云图
def CreateWordCloud(wordList, back_img=None, savefile=None):
    wordcloud_list = ' '.join(wordList)
    font = r'苏新诗柳楷简.ttf' 

    # 无底图
    if back_img == None:
        wc = WordCloud(background_color='white', width=500, height=500, font_path=font)
        wc.generate(wordcloud_list)
        wc.to_file(savefile)

    # 有底图
    else:
        img = Image.open(back_img)
        w, h = img.size
        back_color = np.array(Image.open(back_img))
        wc = WordCloud(background_color = 'white', font_path = font, max_words = 500,
                      mask=back_color, max_font_size = 200, random_state=1)
        wc.generate(wordcloud_list)
        wc.to_file(savefile)
        image_colors = ImageColorGenerator(back_color)
    print("saved to {}".format(savefile))


# 词频计数
def WordCount(string):
    wordList = CutWords(string)
    wordDict = {}

    for word in wordList:
        if len(word) <= 1 or word in stopwords2:
            continue
        if word not in wordDict:
            wordDict[word] = 1
        else:
            wordDict[word] += 1
    return wordDict


# 获得词频最高的十个词
def TopTen(wordDict):
    wordList =sorted(wordDict.items(), key=lambda d:d[1], reverse = True)
    return wordList[0:10]


# 指定关键词词频折线图
def DrawKeyWord(wordList, lineColor):
    myfont = fm.FontProperties(fname = r'msyh.ttc')

    x = np.arange(1, 10, 1)
    xticks = [1, 4, 7]

    ax = plt.subplot(1, 1, 1, facecolor='white')
    ax.set_xticks(xticks)
    ax.set_xticklabels(labels = pathList)

    for i in range(len(wordList)):
        word = wordList[i]
        wordCnt = []
        print(word)
        for Dict in wordCntDictList:
            if word in Dict:
                wordCnt.append(Dict[word])
            else:
                wordCnt.append(0)
        print(wordCnt)
        ax.plot(x, wordCnt, alpha = 0.5, linestyle='--', color = lineColor[i], label = word)
    ax.legend(prop = myfont)
    plt.savefig('words.jpg', dpi=400)
    plt.show()


if __name__ == '__main__':
    Readin()

    DrawPagesCount()

    # 获得头版文章标题词云
    firstPageList = CutWords(firstPageTitles)
    CreateWordCloud(firstPageList, 'background.jpg', 'allword.jpg')
    
    # 每旬的词频统计
    cnt = 1
    for string in allTitles:
        wordDict = WordCount(string)
        wordCntDictList.append(wordDict)
        topTen = TopTen(wordDict)
        pd.DataFrame(topTen).to_csv('topten{}.csv'.format(cnt), encoding='utf_8_sig')
        cnt += 1
    

    keyword = ['疫情','防控','肺炎','复工','复产','脱贫']
    color = ['r','r','r','g','g','b']
    DrawKeyWord(keyword, color)