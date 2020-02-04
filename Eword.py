# -*- coding: utf-8 -*-
import tkinter
import tkinter.messagebox
import pandas as pd
import numpy as np
import os
from tkinter import filedialog
import youdaoread
from playsound import playsound
import copy
import configparser

cp = configparser.ConfigParser()

# 单词被选中次数的权重：weight_cou
# 单词记错次数的权重：weight_err
# 单词基础分：point

if os.path.exists("config.ini"):
    cp.read("config.ini")
    weight_cou = float(cp.get("weight", "weight_count"))
    weight_wrg = float(cp.get("weight", "weight_wrong"))
    point= float(cp.get("weight", "weight_point"))
    yd = youdaoread.youdao(cp.get("address", "address_youdao"))
else:
    weight_cou = 0.3
    weight_wrg = 0.7
    point=1
    # 加载有道
    yd = youdaoread.youdao()

connect=0
glb = 0
cwrong_judge=0

def load():
    global data
    global data_address
    selectFile = tkinter.filedialog.askopenfilename()
    data = pd.read_csv(selectFile, encoding='gbk')
    name1=os.path.split(str(selectFile))[1]
    name2=name1[0:(len(name1)-4)]
    filename.delete(0.0, 'end')
    filename.insert('end', name2)
    data_address=selectFile

def select():
    #设置一个概率表
    global glb
    global connect
    global cwrong_judge
    cwrong_judge=0
    length=len(data['eword'])
    if glb==0:
        #标准化计数
        temp=copy.deepcopy(data)
        #计算单词被选中的得分
        temp['glb0']=temp['count']*weight_cou+temp['wrong']*weight_wrg+point
        maxglb=max(temp['glb0'])
        minglb=min(temp['glb0'])
        if maxglb==minglb:
            temp['glb']=1/length
        else:
            temp['glb']=temp['glb0']/sum(temp['glb0'])
        #得到概率表
        glb=list(temp['glb'])
    #清空上一次的结果
    answer.delete(0.0, 'end')
    answer.insert('end', "...")
    spell.delete(0.0, 'end')
    cword.delete(0.0, 'end')
    #根据概率表进行随机抽取
    x=np.random.choice(range(length),p=glb)
    connect=x

#读单词
def read():
    word=data.loc[connect,'eword']
    word2=word.split(" ")
    for w in word2:
        yd.down(w)
    for w in word2:
        source_file_path="E:/youdaoread/Speech_US/"+w+".mp3"
        playsound(source_file_path)

#显示英文拼写，并判断对错
def showe():
    word=data.loc[connect,'eword']
    answer.delete(0.0, 'end')
    answer.insert('end',word)
    word=word.lower()
    uspell=spell.get(0.0,tkinter.END)
    uspell=uspell.lower().rstrip()
    # print(word,"&&&",uspell,"&&&")
    data.loc[connect, 'count']=data.loc[connect, 'count']+1
    if word!=uspell:
        data.loc[connect, 'wrong']=data.loc[connect, 'wrong']+0.5
        spell.delete(0.0, 'end')
        spell.insert('end',uspell,'wrong')
    else:
        spell.delete(0.0, 'end')
        spell.insert('end', uspell, 'zc')

#显示中文意思及历史错误率
def showc():
    p = round(data.loc[connect, 'prob'] * 100, 2)
    cword.insert('end',str(data.loc[connect, 'cword']) +'\n\n'+ '错误率：' + str(p) + '%')

#中文意思记错，增加错误率
def cwrong():
    global cwrong_judge
    if cwrong_judge==0:
        data.loc[connect, 'wrong']=data.loc[connect, 'wrong']+0.5
        cwrong_judge=1



mygui=tkinter.Tk()
mygui.title('EWORD')
sw = mygui.winfo_screenwidth()
sh = mygui.winfo_screenheight()

ww = 1024
wh = 600
xx = (sw-ww) / 2
yy = (sh-wh) / 2
mygui.geometry('%dx%d+%d+%d'%(ww,wh,xx,yy))
# text=Text(width=30,height=3)

fm1=tkinter.Frame()
fm1.pack(side='top',expand='yes',pady=20)

fm11=tkinter.Frame(fm1)
fm11.pack(side='top',expand='yes',pady=20)

fm12=tkinter.Frame(fm1)
fm12.pack(side='top',expand='yes',pady=20)

fm2=tkinter.Frame()
fm2.pack(side='top',expand='yes',pady=20)

fm21=tkinter.Frame(fm2)
fm21.pack(side='left', fill='x', expand='yes',padx=10)

fm22=tkinter.Frame(fm2)
fm22.pack(side='right', fill='x', expand='yes')

fm3=tkinter.Frame()
fm3.pack(side='top',expand='yes',pady=20)

label=tkinter.Label(fm11,text='听力词汇记记记',font=("黑体", 25, "bold")).pack(anchor='center',expand='yes')

loadfile=tkinter.Button(fm12,text='输入文件',width=20,height=2,command=load,font=("黑体", 15, "bold")).pack(side='left',expand='yes',padx=10)
filename = tkinter.Text(fm12,width=20,height=2,font=("黑体", 15, "bold"))
filename.pack(expand='yes')


#所抽取的单词
read=tkinter.Button(fm21,text='听',width=19,height=1,command=read,font=("黑体", 20, "bold")).pack(pady=5)
#答案
answer = tkinter.Text(fm21,width=20,height=2,font=("黑体", 20, "bold"))
answer.insert('end',"请抽取单词~")
answer.pack(anchor='center',side='top',expand='yes')
#填写
spell = tkinter.Text(fm21,width=20,height=2,font=("黑体", 20, "bold"))
spell.pack(anchor='center',side='top',expand='yes')

spell.tag_add('wrong','0.0') #申明一个tag
spell.tag_config('wrong',foreground='red') #设置tag即插入文字的大小,颜色等
spell.tag_add('zc','0.0') #申明一个tag
spell.tag_config('zc',foreground='black') #设置tag即插入文字的大小,颜色等

#中文意思
cword = tkinter.Text(fm22,width=20,height=6,font=("黑体", 20, "bold"))
cword.pack(anchor='center',side='top',expand='yes')

bx=10
bh=2
next=tkinter.Button(fm3,text='抽词',width=bx,height=bh,command=select,font=("黑体", 20, "bold")).pack(side='left',expand='yes')

seword=tkinter.Button(fm3,text='显示单词',width=bx,height=bh,command=showe,font=("黑体", 20, "bold")).pack(side='left',expand='yes')

scword=tkinter.Button(fm3,text='显示中文',width=bx,height=bh,command=showc,font=("黑体", 20, "bold")).pack(side='left',expand='yes')

cmwrong=tkinter.Button(fm3,text='中文记错',width=bx,height=bh,command=cwrong,font=("黑体", 20, "bold")).pack(side='left',expand='yes')

mygui.mainloop()

# 错误率清算
length=len(data['eword'])
for word in range(length):
    if data.loc[word,'count']==0:
        data.loc[word, 'prob']=0
    else:
        data.loc[word,'prob'] = data.loc[word,'wrong'] / data.loc[word,'count']
data.to_csv(data_address,encoding='gbk',index=False)