
import re 
import os 
import pandas as pd 

# user-defined function 
from utils.utils import *
# from utils.preprocessing import *

def main():  
    # data preparation
    INFO = os.path.join('./data', '인공지능과미래산업특강_출석부.xlsx')
    JOINED = os.path.join(
        './data', 'JoinedParticipants-[Week16_1215]_hangugriseoci_gimgiju_sangmu.xlsx')
    POLLS = os.path.join(
        './data', 'Polls-per-user-[Week16_1215]_hangugriseoci_gimgiju_sangmu.xlsx')


    SAVE = True  # True 저장
    START_DATE = '2021-12-15'
    END_DATE = '2021-12-15 17:20:00'


    # read excel
    info_table = pd.read_excel(INFO)  # students' personal info.
    feed_df = pd.read_excel(POLLS).iloc[1:]  # feed back
    joined_df = pd.read_excel(JOINED)
    feed_list = list(feed_df.columns)  # for etract today quizs


    # -------------
    # preprocessing
    # -------------
    # Name --> rid of blank strip, and lower
    feed_df = feed_df.fillna('anonymous')
    feed_df[feed_list[5]] = feed_df[feed_list[5]].str.replace(' ', '')
    feed_df[feed_list[5]] = feed_df[feed_list[5]].str.strip()
    feed_df[feed_list[5]] = feed_df[feed_list[5]].str.lower()

    # Participant Name --> Name, Student ID
    feed_df['Name'] = feed_df['User Name'].apply(extract_kor)
    feed_df['Name'] = feed_df['Name'].str.lower()
    feed_df['Name'] = feed_df['Name'].str.strip()


    # fill out the Name from INFO
    feed_df['Student ID'] = feed_df['User Name'].apply(extract_id)
    feed_df_anony = feed_df[feed_df['User Name'] == 'anonymous']
    feed_df = feed_df[feed_df['User Name'] != 'anonymous']
    feed_df_anony['Name'] = list(feed_df_anony[feed_list[5]].values)
    feed_df_anony['Student ID'] = list(feed_df_anony[feed_list[6]].values)
    feed_df = pd.concat([feed_df, feed_df_anony], axis=0)
    feed_df_anony = feed_df[feed_df['Name'] == 'anonymous']
    feed_df = feed_df[feed_df['Name'] != 'anonymous']
    feed_df_anony[feed_df_anony['Name'] == 'anonymous']
    feed_df_anony['Name'] = list(feed_df_anony[feed_list[5]].values)
    feed_df_anony['Student ID'] = list(feed_df_anony[feed_list[6]].values)
    feed_df = pd.concat([feed_df, feed_df_anony], axis=0)

    # 학번 안넣은사람 찾아주기...
    feed_df_noid = feed_df[feed_df['Student ID'] == '']
    feed_df = feed_df[feed_df['Student ID'] != '']
    feed_df_noid['Student ID'] = list(feed_df_noid[feed_list[6]].values)
    feed_df = pd.concat([feed_df, feed_df_noid], axis=0)

    # 학번 오류찾기
    feed_df['학번기입정상여부'] = feed_df['Student ID'].apply(count_ID_length)
    feed_df = feed_df[feed_df['학번기입정상여부'] != '학번기입오류']
    feed_df['Student ID'] = feed_df['Student ID'].astype(int)  # int로 변경
    feed_df['Name'] = feed_df['Name'].str.replace(' ', '')
    feed_df['Name'] = feed_df['Name'].str.strip()
    feed_df['Name'] = feed_df['Name'].str.lower()

    # set quiz columns
    quiz_columns = ['Name', 'Student ID', feed_list[4], feed_list[8], feed_list[9]]
    feed_columns = ['Name', 'Student ID', feed_list[-1]]


    # -------------
    # Quiz
    # -------------
    quiz_df = feed_df[quiz_columns]
    num = quiz_df[quiz_df['Total Correct Answers'] != 2].shape[0]

    # save
    if SAVE:
        quiz_df.to_excel(f'./results/{START_DATE}_quiz.xlsx', encoding='utf-8')

    # -------------
    # Attendance
    # -------------
    joined_df['Joined at'] = joined_df['Joined at'].astype('datetime64[ns]')
    joined_df = joined_df.sort_values('Joined at')
    joined_df = joined_df[(START_DATE < joined_df['Joined at'])
                          & (joined_df['Joined at'] < END_DATE)]

    # Participant Name --> Name, Student ID
    joined_df['Name'] = joined_df['Participant Name'].apply(extract_kor)
    joined_df['Student ID'] = joined_df['Participant Name'].apply(extract_id)
    joined_df = joined_df[(START_DATE < joined_df['Joined at'])
                          & (joined_df['Joined at'] < END_DATE)]
    joined_df['Name'] = joined_df['Name'].str.replace(' ', '')
    joined_df['Name'] = joined_df['Name'].str.strip()
    joined_df['Name'] = joined_df['Name'].str.lower()

    # 중복접속은 출석 불인정
    tmp = joined_df[joined_df['Name'] != 'anonymous']  # delete Anonymous
    # remove duplicate and remain early access
    tmp = tmp[tmp['Participant Name'].duplicated() == False]

    # save
    if SAVE:
        tmp.to_excel(f'./results/{START_DATE}_attendance.xlsx', encoding='utf-8')

    # StudentID 찾기
    id_dict = {}
    for name in tmp[tmp['Student ID'] == '']['Name'].values:
        try:
            id_dict[name] = info_table[info_table['Name']
                                       == name]['Student ID'].values[0]
        except:
            print('error:', name)

    for key, value in id_dict.items():
        tmp.loc[tmp['Name'] == key, 'Student ID'] = value

    count = 0
    set_b = {}
    for i in info_table['Student ID'].values:
        if str(i).strip() not in tmp['Student ID'].values:
            count += 1
            set_b[info_table[info_table['Student ID'] == i]['Name'].values[0]] = i

    count = 0
    set_a = {}
    for i in info_table['Name'].values:
        if str(i).strip().replace(' ', '') not in tmp['Name'].values:
            count += 1
            set_a[i] = info_table[info_table['Name'] == i]['Student ID'].values[0]

    absent = list(set(set_a.keys()).intersection(set(set_b.keys())))
    absent_df = info_table[info_table['Name'].isin(absent)]

    # save
    if SAVE:
        num = absent_df.shape[0]
        absent_df.to_excel(
            f'./results/{START_DATE}_absence_{num}.xlsx', encoding='utf-8')

    # -----------
    # FeedBack
    # -----------
    feed = feed_df[feed_columns]
    feed[[feed_list[-1]]] = feed[[feed_list[-1]]].astype(str)
    tmp = feed.columns[-1]
    feed['글자수'] = feed[tmp].apply(count_word)

    # save
    if SAVE:
        feed.to_excel(f'./results/{START_DATE}_feedback.xlsx', encoding='utf-8')
        feed[feed['글자수'] == '충족'].to_excel(
            f'./results/{START_DATE}_feedback_O.xlsx')


    # -----------
    # Final_report
    # -----------
    report_df = info_table[['Student ID', 'Name', '소속', 'Dep.', 'email']]
    report_df[START_DATE+'-Attend'] = report_df['Name'].apply(fill_absent)

    # FeedBack
    feed['TONUM'] = feed['글자수'].apply(conver2num)
    feed.columns = ['Name', 'Student ID',
                    'Feedback', '글자수', START_DATE+'-FeedBack']

    report_df = pd.merge(report_df, feed[['Name', 'Student ID',
                         START_DATE + '-FeedBack']],
                         how='left').fillna(-1)
    # Quiz 
    quiz_df.columns =  ['Name', 'Student ID', START_DATE+'-Quiz','-1', '-2'+'-3']

    report_df = pd.merge(report_df,
                      quiz_df[['Name', 'Student ID',
                               START_DATE+'-Quiz']],
                      how='left').fillna(-1)


    report_df = report_df.drop_duplicates()
    report_df.to_excel(f'./results/report_{START_DATE}.xlsx',encoding='utf-8',index=False)
    return None 

if __name__ == "__main__":
    main()
 
