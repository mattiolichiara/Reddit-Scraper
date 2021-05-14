import praw
import pandas
from IPython import display
import math
from pprint import pprint
import numpy as np
import nltk
import string, re
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim.parsing.preprocessing import remove_stopwords
from gensim.parsing.preprocessing import STOPWORDS
import prawcore
import os
import os.path
import csv
from nltk.stem import WordNetLemmatizer
sns.set(style='darkgrid', context='talk', palette='Dark2')




##***API's Auth***##
reddit = praw.Reddit(client_id='**************', client_secret='**************', user_agent='**************')




##***Basic Settings***##
headlines = set()
writingSubs = set()

'''try:
    print("-------------------------------------------------------------------------------------------")
    user_s = input("Enter User: \n")
    print("-------------------------------------------------------------------------------------------\n")
except NotFound:
    print("Invalid Username")'''

user = reddit.redditor('imveryfontofyou')
fileNameComments = str(user)




##***RETRIEVING USER COMMENTS***##
#commentsNEW = []
for comment in user.comments.new(limit=None):
  #commentsNEW.append([comment.body, comment.score, comment.subreddit])
  headlines.add(comment.body.lower())
  writingSubs.add(str(comment.subreddit))




##***Printing Comments' Total Number***##
totalComments = len(headlines)
print("-------------------------------------------------------------------------------------------")
print('Total Number of Analysed Comments: '+str(totalComments))
print("-------------------------------------------------------------------------------------------")

#commentsNEW = pandas.DataFrame(commentsNEW, columns=['COMMENT', 'SCORE', 'SUBREDDIT'])
#print (commentsNEW)
#print("-------------------------")
#commentsNEW.to_csv(fileNameComments)




##***Applying STOP WORDS DataSet***##
clearedComments = []
for line in headlines:
    clearedComments.append(remove_stopwords(line.translate(str.maketrans({a:None for a in string.punctuation}))))

'''print("\n-------------------------------------------------------------------------------------------")
print(clearedComments)
print("-------------------------------------------------------------------------------------------\n\n")'''




##***DATA CATEGORIZATION***##
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

sia = SIA()
results = []

for clearedComment in clearedComments:
    polarity_score = sia.polarity_scores(clearedComment)
    polarity_score['comment'] = clearedComment
    results.append(polarity_score)

#pprint(results[:100], width=100)




##***DATA LABELING***##
dataFrame = pandas.DataFrame.from_records(results)
dataFrame['label'] = 0
dataFrame.loc[dataFrame['compound'] > 0.3, 'label'] = 1
dataFrame.loc[dataFrame['compound'] < -0.3, 'label'] = -1

dataFrame2 = dataFrame[['comment', 'label']]

if os.path.exists('./UsersData/SentimentAnalysis/'+fileNameComments+'_reddit_comments_labels.csv'):
    os.remove('./UsersData/SentimentAnalysis/'+fileNameComments+'_reddit_comments_labels.csv')


dataFrame2.to_csv('UsersData/SentimentAnalysis/'+fileNameComments+'_reddit_comments_labels.csv', mode='a', encoding='utf-8', index=True)
print(str(dataFrame))




##***Storage Categorization***##
'''print("Positive comments:\n")
pprint(list(dataFrame[dataFrame['label'] == 1].comment)[:5], width=200)

print("\nNegative comments:\n")
pprint(list(dataFrame[dataFrame['label'] == -1].comment)[:5], width=200)

print("\nNeutral comments:\n")
pprint(list(dataFrame[dataFrame['label'] == 0].comment)[:5], width=200)'''




##***Percentage Calculation and Print***##
print("\n-------------------------------------------------------------------------------------------")
#print(dataFrame.label.value_counts())
print("Categories percentage:")
print("-------------------------------------------------------------------------------------------")
print(dataFrame.label.value_counts(normalize=True) * 100)
print("-------------------------------------------------------------------------------------------\n")




##***Recourring Positive Words Count and Retrieving***##
fullString = ""
my_stopwords = ['better', 'yeah', 'actually', 'like', 'bad', 'bit', 'lot',
                 'change', 'completely', 'im', 'youre', 'day', 'didnt',
                'different', 'why', 'dont', 'got', 'havent', 'hope', 'ive',
                 'know', 'need', 'new', 'people', 'pick', 'she', 'stick',
                 'talk', 'thank', 'you', 'he', 'they', 'thanks', 'thats',
                 'there', 'thing', 'think', 'try', 'undestrand', 'waiting',
                  'yes', 'no', 'maybe', 'years', 'good', 'best', 'doesnt',
                  'dont', 'get', 'getting', 'going', 'go', 'went', 'kind', 'love'
                  'low', 'high', 'makes', 'pretty', 'probably', 'sure', 'theyre',
                  'use', 'want', 'way', 'agree', 'big', 'buddy', 'bunch', 'case',
                  'card', 'cause', 'cool', 'dude', 'compare', 'deep', 'definitely',
                  'det', 'detail', 'gave', 'give', 'grab', 'hand', 'having', 'heh',
                  'idea', 'me', 'modern', 'old', 'real', 'reason', 'regular',
                  'said', 'saying', 'say', 'set', 'get', 'someone', 'somebody',
                  'some', 'super', 'totally', 'truly', 'truth', 'way', 'wish', 'wonder',
                  'things', 'arent', 'theres', 'ill', 'youll', 'giving', 'shes', 'hes', 'i', 'great']
#print(my_stopwords)
keyWords = []
lemmatized_noun=[]
lemmatized_verb=[]
lemmatized=[]
positiveComments = list(dataFrame[dataFrame.label == 1].comment)

for positiveComment in positiveComments:
    fullString+=(positiveComment+" ")

#Lemmatization and Tokenization
lemmatizer = WordNetLemmatizer()

tokenized = word_tokenize(fullString)

for tk in tokenized:
    lemmatized_noun.append(lemmatizer.lemmatize(tk))#noun

for ln in lemmatized_noun:
    lemmatized_verb.append(lemmatizer.lemmatize(ln, pos='v'))#verb

for lv in lemmatized_verb:
    lemmatized.append(lemmatizer.lemmatize(lv, pos='a'))#adjective

recourringPosWords = nltk.FreqDist(lemmatized)
keyWords = recourringPosWords.most_common(100)

searchWords = [i[0] for i in keyWords]

for word in my_stopwords:
    index=-1
    for key in searchWords:
        index+=1
        if word == key:
            searchWords.pop(index)
            keyWords.pop(index)
            #print("word: "+word+" - key: "+key)

searchWords += writingSubs
#print(searchWords)

print("\n-------------------------------------------------------------------------------------------")
print("100 Most Common Positive Words by User:")
print("-------------------------------------------------------------------------------------------")
print(keyWords)
print("-------------------------------------------------------------------------------------------\n")




##***Subs Recommendation***##
recommendedSubreddits = [set()]
temp = []
temp2 = set()
subreddits = reddit.subreddits
for key in searchWords:
    temp+=subreddits.search_by_name(key, include_nsfw=False)
    print("Finding: "+key)

for t in temp:
    temp2.add(str(t).lower())

recommendedSubreddits = list(temp2)
recommendedSubreddits.sort()

print("\n-------------------------------------------------------------------------------------------")
print("Recommended Subs for User Saved on .csv filw with User Name.")
print("-------------------------------------------------------------------------------------------")
recommendedSubreddits = pandas.DataFrame(recommendedSubreddits,columns=['SUBREDDIT'])

if os.path.exists('./UsersData/Recommendations/'+fileNameComments+'.csv'):
    os.remove('./UsersData/Recommendations/'+fileNameComments+'.csv')

recommendedSubreddits.to_csv("UsersData/Recommendations/"+fileNameComments+".csv", mode='a', encoding='utf-8', index=True)
print(recommendedSubreddits)
print("-------------------------------------------------------------------------------------------\n")




##***Overwatch Buyer***##
ow_related = ['qp', 'quickplay', 'quick', 'play', 'classic', 'arcade', 'deathmatch', 'mystery', 'heroes', 'comp',
              'competitive', 'overwatch', 'league', 'top500', 'bronze', 'silver', 'gold', 'plat', 'diamond', 'master',
              'grandmaster', 'tank', 'tanks', 'shield', 'shields' 'off tank', 'main tank', 'off-tank', 'd.va', 'orisa', 'reinhart',
              'roadhog', 'sigma', 'winston', 'wrecking ball', 'hammond', 'monkey', 'cooldown', 'cooldowns', 'zarya', 'healer',
              'healers', 'support', 'role', 'roles', 'queue', 'open', 'supports', 'peel', 'ana', 'baptiste', 'brigitte', 'fps',
              'game', 'play', 'op', 'lucio', 'lùcio', 'mercy', 'moira', 'zenyatta', 'aim', 'accuracy', 'headshot', 'headshots',
              'dps', 'damage', 'kills', 'sens', 'dpi', 'mouse', 'hitscan', 'projectile', 'mobility', 'ult', 'q', 'ultimate', 'team',
              'enemy', 'enemy team', 'sr', 'ashe', 'bastion', 'doomfist', 'echo', 'genji', 'hanzo', 'junkrat', 'mccree', 'mei',
              'pharah', 'reaper', 'soldier 76', 'soldier', 'hog', 'doom', 'sombra', 'symmetra', 'turret', 'turrets', 'torb', 'torbjorn',
              'potg', 'highlight', 'play of the game', 'tracer', 'widow', 'widowmaker', 'map', 'maps', 'assalut', '2cp', 'payload', 'point',
              'stall', 'control', 'ilios', 'busan', 'lijiang tower', 'lijiang', 'nepal', 'oasis', 'hanamura', 'horizon',
              'paris', 'temple of anubis', 'anubis', 'volskaya', 'volskaya industries', 'dorado', 'havana', 'junkertown', 'rialto',
              'route 66', 'gibraltar', 'watchpoint gibraltar', 'blizzard', 'jeff kaplan', 'jeff', 'kaplan', 'papa jeff', 'blizzard world',
              'eichenwalde', 'hollywood', 'kings row', 'numbani', 'castillo', '1v1', 'petra',  'fps', 'multiplayer', 'shooter',
              'scope', 'kill', 'k/d', 'k/d ratio', 'objective', 'xp', 'hp', 'arena', 'ability', 'abilities', 'MMO', 'mmo', 'pulse', 'bomb',
              'bob', 'deadeye', 'nano', 'barrage', 'shatter', 'bongo', 'matrix', 'rally', 'blade', 'dragon', 'tire', 'beat', 'valk',
              'valkyrie', 'coalescence', 'blossom', 'death', 'visor', 'tac visor', 'emp', 'mines', 'grav', 'trans', 'transcendence',
              'sleep', 'nade', 'dynamite', 'gun', 'stun', 'whip', 'deflect', 'envirmental', 'boop', 'fan the hammer', 'freeze', 'pistol',
              'halt', 'rockets', 'rocket', 'hammer', 'pinned', 'charge', 'charging', 'hook', 'rock', 'hack', 'hacked', 'teleport', 'blink',
              'recall', 'grapple', 'venom', 'mine', 'barrier', 'primal', 'discord', 'harmony', 'orb', 'healing', 'bubble', 'graviton', 'tp']

fullComment = ""
lemmatizedG_noun=[]
lemmatizedG_verb=[]
lemmatizedG=[]
OWdata = list(dataFrame.comment)
#print(OWdata)
for dt in OWdata:
    fullComment+=(dt+" ")

tokenizedG = word_tokenize(fullString)
GamingWords = tokenizedG

for gw in GamingWords:
    lemmatizedG_noun.append(lemmatizer.lemmatize(gw))#noun

for ln in lemmatizedG_noun:
    lemmatizedG_verb.append(lemmatizer.lemmatize(ln, pos='v'))#verb

for lv in lemmatizedG_verb:
    lemmatizedG.append(lemmatizer.lemmatize(lv, pos='a'))#adjective

Remaining_words = []

for word in my_stopwords:
    index=-1
    for gm in lemmatizedG:
        index+=1
        if word == gm:
            lemmatizedG.pop(index)
            #print("word: "+word+" - gm: "+gm)

print("\n-------------------------------------------------------------------------------------------")
print("Study of User interest about Overwatch Gaming.")
print("-------------------------------------------------------------------------------------------")

words_len = len(GamingWords)
print("Total number of Words: "+str(words_len))

for word in ow_related:
    for gm in lemmatizedG:
        if word==gm:
            Remaining_words.append(gm)

correlated_len = len(Remaining_words)
print("Number of Correlated Words: "+str(correlated_len))

ow_percentage = (correlated_len/words_len)*100

print("Percentage of Game Interest: "+str(ow_percentage))

if ow_percentage>3:
    labelGM=1
else:
    labelGM=-1

ow_percentage = float("{:.2f}".format(ow_percentage))

print("Buyer Label: "+str(labelGM))
print("-------------------------------------------------------------------------------------------\n")

#print(Remaining_words)

recourringGaming = nltk.FreqDist(Remaining_words)
keyGamingWords = recourringGaming.most_common()

print("\n-------------------------------------------------------------------------------------------")
print("Overwatch Related Words Frequency.")
print("-------------------------------------------------------------------------------------------")
print(keyGamingWords)
print("-------------------------------------------------------------------------------------------")




##***SA PLOT***##
fig, ax = plt.subplots(figsize=(6, 6))

counts = dataFrame.label.value_counts(normalize=True) * 100

sns.barplot(x=counts.index, y=counts, ax=ax)

ax.set_xticklabels(['Negative', 'Neutral', 'Positive'])
ax.set_ylabel("Percentage")

#plt.show()
if os.path.exists('./UsersData/SentimentAnalysis/'+fileNameComments+'SA.png'):
    os.remove('./UsersData/SentimentAnalysis/'+fileNameComments+'SA.png')

plt.savefig('UsersData/SentimentAnalysis/'+fileNameComments+'SA.png')
plt.clf()



#CW PLOT
labels = 'Total Words', 'Correlated'
sizes = [(100-ow_percentage), ow_percentage]
colors = ['purple', 'lightskyblue']
explode = (0, 0.1)
# Plot
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)

plt.axis('equal')
#plt.show()
if os.path.exists('./UsersData/Buyers/'+fileNameComments+'CW.png'):
    os.remove('./UsersData/Buyers/'+fileNameComments+'CW.png')

plt.savefig('UsersData/Buyers/'+fileNameComments+'CW.png')





#Updating Buyers CSV
if labelGM!=-1:
    UserGM=[[fileNameComments,words_len,correlated_len,ow_percentage,labelGM]]
    dfGM = pandas.DataFrame(UserGM, columns=['User','Total Words','Correlated Words','Percentage','Buyer Label'])

    if os.path.exists('./UsersData/Buyers/Buyers.csv'):
        f = open('UsersData/Buyers/Buyers.csv', 'a')
        dfGM.to_csv(f, header=f.tell()==0, index=False)
    else:
        dfGM.to_csv('UsersData/Buyers/Buyers.csv', mode='a', encoding='utf-8', index=False)
