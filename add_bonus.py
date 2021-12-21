
import re
import os 
import pandas as pd
from collections import Counter

def extract_kor(string):
    '''extract korean in string'''
    string = str(string)
    kor= "[^가-힣ㄱ-ㅎㅏ-ㅢ-a-z-A-Z]" 
    result1 = re.sub(kor, '', string)
    result1.replace(' ','')
    return result1.strip()


def main():
    
    df = pd.read_excel('./results/KU_인공지능과미래산업특강_가산점.xlsx').drop('Unnamed: 0',axis=1)
    *_,days = df.shape

    total_list = []
    for day in range(days):
        tmp_list = df.iloc[:,day].map(lambda x : extract_kor(x))
        total_list.extend(tmp_list.values)

    counted = Counter(total_list)
    df_counted = pd.DataFrame.from_dict(counted, orient='index').reset_index()
    df_counted.columns = ['Name','count']
    df_counted=df_counted[df_counted['Name']!='nan']
    df_counted.to_excel('./results/final_thumpsup.xlsx',encoding='utf-8', index=False)
    return None 

if __name__ == "__main__":
    main()
