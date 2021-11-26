import re
import pandas as pd

# 将整篇文章进行分段
def segments(url):
    raw = pd.read_csv(url,names=['txt'], sep='aaa', encoding="GBK" ,engine='python')

    def m_head(tem_str):
        return tem_str[:1]

    def m_mid(tmp_str):
        return tmp_str.find("回 ")
    raw['head'] = raw.txt.apply(m_head)
    raw['mid'] = raw.txt.apply(m_mid)
    raw['len'] = raw.txt.apply(len)
    chap_num = 0
    for i in range(len(raw)):
        if raw['head'][i] == "第" and raw['mid'][i] > 0 and raw['len'][i] < 30:
            chap_num += 1
        if chap_num >= 40 and raw['txt'][i] == "附录一：成吉思汗家族":
            chap_num = 0
        raw.loc[i, 'chap'] = chap_num
    del raw['head']
    del raw['mid']
    del raw['len']
    tmp_chap = raw[raw['chap'] == 7].copy()
    tmp_chap.reset_index(drop=True, inplace=True)
    tmp_chap['paraidx'] = tmp_chap.index
    paragraph = tmp_chap['txt'].values.tolist()
    return paragraph

# 将每段进行分句
def cut(para):
    # 相关规则
    pattern = ['([。！？\?])([^”’])','(\.{6})([^”’])','(\…{2})([^”’])','([。！？\?][”’])([^，。！？\?])']
    for i in pattern:
        para = re.sub(i, r"\1\n\2", para)
    para = para.rstrip()
    return para.split("\n")

# 将其中被错分的语句进行连接(主要是针对话语)
def connect(paragraph):
    sentence_before = []
    sentence_after = []
    for each_para in paragraph:
        sentence_before.append(cut(each_para))
    # 核心代码！（将被错分的语句进行连接）
    for each in sentence_before:
        list = []
        sentence = ""
        FLAG = True # 非常关键！判断有'：“'的符号后面的语句是否继续拼接
        for i in each:
            if i.find('：“') * i.find('”') >= 0 and FLAG:
                list.append(i + sentence)
            else:
                FLAG = False
                sentence = sentence + i
                if i.find('”') > 0:
                    list.append(sentence)
                    sentence = ""
                    FLAG = True
        sentence_after.append(list)
    return sentence_after

# 将最后的结果保存到DataFrame
def toDataFrame(list3):
    df = pd.DataFrame(columns=["content","paragraph","sentence"])
    for para_num,i in enumerate(list3):
       for sentence_num,j in enumerate(i):
            df_ = pd.DataFrame({"content": j, "paragraph": para_num,"sentence":sentence_num+1},index=[para_num])
            df = df.append(df_,ignore_index=True)
    for i in df['content'].values.tolist():
        print(i)

def main():
    # URL = "/Users/dengzhao/Downloads/金庸-射雕英雄传txt精校版.txt"
    #C:\Users\hp\Desktop\1
    URL = input("请输入文件地址：")
    para = segments(URL)
    result = connect(para)
    print(result)
    flag = input("以DataFrame形式输出数据(Y,N)：")
    if flag == 'Y':
        toDataFrame(result)
    elif flag == 'N':
        print("Thanks！！！！")
    else:
        print("程序结束！请检查的你的输入！")

if __name__ == '__main__':
    main()
