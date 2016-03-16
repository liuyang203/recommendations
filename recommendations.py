# -*- coding: utf-8 -*-
__author__ = 'Liu'


from math import sqrt


#一个涉及影评者及其对几部影片评分情况的字典（嵌套）
critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                  'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                  'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                     'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                         'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                     'The Night Listener': 4.5, 'Superman Returns': 4.0,
                     'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                     'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                     'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                      'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}
}
'''
#计算任意两人间的相似度评价值 By欧几里得距离评价
def sim_distance(dict, person1, person2):
    si = {}
    for item in dict[person1]: #找出二者相同之处
        if item in dict[person2]:
            si[item] = 1
    #print si
    if len(si) == 0: return 0   #二者没有共同之处，返回0

    #计算所有差值的平方和--欧几里得距离评价要开根号
    sum_of_squares = sum([pow(dict[person1][item]-dict[person2][item],2)
                          for item in dict[person1] if item in dict[person2]])

    return 1/(1+sqrt(sum_of_squares))
'''

#欧几里得
def sim_distance(dict, person1,person2):
    si = {}
    for item in dict[person1]:
        if item in dict[person2]:
            si[item] = 1

    if len(si) == 0: return 0

    result =sum(pow(dict[person1][item]-dict[person2][item],2)
                for item in si)
    return 1/(1+sqrt(result))
#皮尔逊
def sim_pearson(dict, p1, p2):
    si = {}
    for item in dict[p1]:
        if item in dict[p2]:
            si[item] = 1
    #得到列表元素个数
    n = len(si)
    #二者无共同之处，则返回1
    if n == 0: return 1

    #对所有偏好求和
    sum1 = sum([dict[p1][item] for item in si])
    sum2 = sum([dict[p2][item] for item in si])

    #求平方和
    sum1Sq = sum([pow(dict[p1][item],2) for item in si])
    sum2Sq = sum([pow(dict[p2][item],2) for item in si])

    #求乘积之和
    pSum = sum([dict[p1][item] * dict[p2][item] for item in si])

    #计算皮尔逊评价值
    num = pSum - (sum1*sum2/n)
    den = sqrt((sum1Sq - pow(sum1, 2)/n) * (sum2Sq - pow(sum2, 2)/n))
    if den == 0: return 0

    r = num/den

    return r


#找出与用户person相似度最高的其他用户列表
#基于人口统计学的推荐
def topMatches(dict, person, n = 5, similarity = sim_pearson):
    scores = [(other,similarity(dict, person, other))
              for other in dict if other != person]
    #对列表scores进行排序
    scores_new = sorted(scores,key=lambda scores: scores[1],reverse= True)

    return  scores_new[0:n]

#print topMatches(critics, 'Toby',n=3)

#利用所有他人对影片的评价值的加权平均，为person提供建议
#基于用户的协同过滤推荐
def getRecommendations(dict, person,similarity = sim_pearson):
    totals = {}
    simSums = {}
    for other in dict:  #other是字典里的键--名字
        if other == person: continue
        sim = similarity(dict, person, other)

        if sim <= 0: continue
        #只对自己还未曾看过的影片进行预测评价
        for item in dict[other]:    #item是影片名
            if item not in dict[person] or dict[person][item] == 0:
                #相似度*评价值
                totals.setdefault(item,0)   #字典中添加键的函数
                #print type(totals)
                totals[item] += sim * dict[other][item]
                #相似度之和
                simSums.setdefault(item,0)
                simSums[item] += sim
    #建立归一化列表
    rankings = [(item,total/simSums[item]) for item, total in totals.items()]
    #排序
    new_rankings = sorted(rankings,key= lambda rankings:rankings[1],reverse= True)

    return new_rankings

def transformDict(dict):
    result = {}
    for person in dict:
        for item in dict[person]:
            result.setdefault(item,{})

            #物品与人员对换
            result[item][person] = dict[person][item]
    return result


#基于物品的协同过滤推荐

#构建一个包含相近物品的数据集
def calculateSimilarItems(dict,n=10):
    result = {}

    #以物品为中心对偏好矩阵进行倒置
    itemDict = transformDict(dict)
    #print itemDict

    c=0
    for item in itemDict:
        #针对大数据集更新状态变量
        c+=1
        if c%100==0: print "%d / %d" % (c,len(itemDict))
        #寻找相似物品
        scores = topMatches(itemDict,item,n=n,similarity=sim_distance)
        result[item]=scores
    return result


def getRecommendedItems(dict,itemsimdict,user):#itemsimdata包含相近物品的数据集
    userRatings = dict[user]
    scores = {}
    totalSim = {}
    #i=0
    #遍历user评分的物品
    for (item, rating) in userRatings.items():
        #i = i + 1

    #遍历与当前物品item相近的物品
        for (item2,simlarity) in itemsimdict[item]:

            #如果该用户以对该物品做过评价，忽略
            if item2 in userRatings: continue
            #评价值与相似度的加权之和
            scores.setdefault(item2,0)
            scores[item2] += simlarity*rating

            #print i
            #print item2,simlarity,'*',rating,"=",
            #print scores[item2]
            #全部相似度之和
            totalSim.setdefault(item2,0)
            totalSim[item2] += simlarity
            #print totalSim[item2]

    #print scores
    #print totalSim
    rankings = [(item,score/totalSim[item]) for item,score in scores.items()]
    new_rankings = sorted(rankings, key=lambda rankings: rankings[1], reverse=True)
    return  new_rankings




'''
print topMatches(critics,'Toby')            #和用户‘Toby’相似度最高的用户列表
print getRecommendations(critics,'Toby')    #推荐用户‘Toby’观看的影片列表及其推荐值
'''
'''
movies = transformDict(critics)
#print movies
print topMatches(movies,'Superman Returns') #和电影超人相似度最高的影片列表
'''
'''
itemsimdict = calculateSimilarItems(critics)    #基于影片相似度的嵌套字典

print getRecommendedItems(critics,itemsimdict,'Toby')   #基于用户看过的影片和影片相似度的嵌套字典
                                                    #给出推荐该用户观看的用户影片列表
'''


def loadMovieLens(path='C:\Users\Administrator'):

    #获取影片标题
    movies = {}
    for line in open(path+'/movies.dat'):
        (id,title)=line.split('::')[0:2]
        movies[id]=title

    #加载数据
        dict = {}
    for line in open(path+'/ratings.dat'):
        (user,movieid,rating,time)=line.split('::')
        dict.setdefault(user,{})
        dict[user][movies[movieid]]=float(rating)
    return dict

#dict = loadMovieLens()
#print getRecommendations(dict,'1')[0:30]

#itemsim = calculateSimilarItems(dict,n=50)
#print getRecommendedItems(dict,itemsim,'1')[0:30]


def sim_tonimoto(dict, user1, user2):
    common = [item for item in dict[user1] if item in dict[user2]]
    return float(len(common))/(len(dict[user1]) + len(dict[user2]) - len(common))












