
import re 
import os 
import pandas as pd 


def extract_kor(string):
    '''extract korean in string'''
    string = str(string)
    kor= "[^가-힣ㄱ-ㅎㅏ-ㅢ-a-z-A-Z]" 
    result1 = re.sub(kor, '', string)
    result1.replace(' ','')
    return result1.strip()

def extract_id(string):
    string  = str(string)
    '''extract student id in string'''
    num =  r"[^0-9]"
    result2 = re.sub(num, '', string)
    return result2.strip()


def count_word(string):
    if len(str(string)) > 50:
        return '충족' 
    else:
        return '부족' 
def make_quiz_report(report_df, quiz_df):
    '''# 미제출 -1 , 정답 0, 1, 2 

    '''
    quiz_df.columns = ['Name', 'Student ID', START_DATE+'-Quiz',
                       '-1',
                       '-2',
                       ]
    tmp['Student ID'] = tmp['Student ID'].astype(int)
    result = pd.merge(report_df,
                      tmp[['Name', 'Student ID',
                               START_DATE+'-Quiz']],
                      how='left').fillna(-1)
    return result

def pprint(lists):
    for i in lists:
        print(i[:15])
    return None

def count_ID_length(x):
    x = str(x).replace(' ','')
    if len(x)==10 and x.isalnum():
        return 1 
    else:
        return '학번기입오류'
    
    
# 출석 
def fill_absent(x, absent_list=absent_df['Name'].values.tolist()):
    if x in absent_list:
        return 0
    else: 
        return 1
    
# 피드백 불성실
def conver2num(x):
    if x == '충족':
        return 1
    elif x =='부족':
        return 0 
    else:
        return -1
