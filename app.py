
import argparse
import pandas as pd

def fill_day(df):
    day = 5
    tmp = []
    for i in df.index:
        tmp.append(day)
        if day == 7:
            day = 1
        else:
            day = day + 1
    df['星期'] = tmp
    return df

def remove_228(df):
    tmp = 0
    while True:
        if df['日期'][tmp] == '2021/02/27':
            break
        else:
            tmp = tmp + 1
    df = df.drop([tmp, tmp+1, tmp+2])
    df = df.reset_index(drop=True)
    return df

def fill_missing_val(df):
    ret = df.copy()
    mar19 = pd.Series({'日期':'2021/03/19', '備轉容量(萬瓩)':327.2, '備轉容量率(%)':10.93, '星期':5, '備轉容量(MW)':3272.0})
    ret = ret.append(mar19, ignore_index=True)

    mar20 = pd.Series({'日期':'2021/03/20', '備轉容量(萬瓩)':307.5, '備轉容量率(%)':11.48, '星期':6, '備轉容量(MW)':3075})
    ret = ret.append(mar20, ignore_index=True)

    mar21 = pd.Series({'日期':'2021/03/21', '備轉容量(萬瓩)':298.3, '備轉容量率(%)':11.44, '星期':7, '備轉容量(MW)':2983})
    ret = ret.append(mar21, ignore_index=True)

    mar22 = pd.Series({'日期':'2021/03/22', '備轉容量(萬瓩)':307.4, '備轉容量率(%)':10.22, '星期':1, '備轉容量(MW)':3074})
    ret = ret.append(mar22, ignore_index=True)

    return ret

def list_by_day(df, end, day):
    lst = []
    for i in range(end):
        if df['星期'][i] == day:
            lst.append(df['備轉容量(MW)'][i])
    return lst

def model(train_df, interval, n):
    day = 2
    ret = []
    for i in range(0, interval):
        mean = 0
        div = 0
        lst = list_by_day(train_df, len(train_df), day)
        lst.reverse()
        
        if day != 7:
            for j in range(len(lst)):
                lst[j] = lst[j] + 70
                if lst[j] < 3000:
                    lst[j] = 3000
        
        if n > len(lst):
            mean = sum(lst) / len(lst)
        else:
            mean = sum(lst[0:n]) / n
        
        ret.append(int(mean))
        if day == 7:
            day = 1
        else:
            day = day + 1
    return ret

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--training',
                       default='training_data.csv',
                       help='input training data file name')

    parser.add_argument('--output',
                        default='submission.csv',
                        help='output file name')
    args = parser.parse_args()
    
    # load training data
    df_training = pd.read_csv(args.training)

    # converte unit
    tmp = []
    for i in range(len(df_training)):
        tmp.append(df_training['備轉容量(萬瓩)'][i] * 10)
    df_training['備轉容量(MW)'] = tmp

    # fill every date's day (1~7)
    df_training = fill_day(df_training)

    # remove 2/27, 2/28, 3/1 from training data
    df_training = remove_228(df_training)

    # fill up to 2021/03/22
    df_training = fill_missing_val(df_training)

    # predict
    pred = model(df_training, 7, 3)

    # save
    df_result = pd.DataFrame()
    df_result['date'] = ['20210323', '20210324', '20210325', '20210326', '20210327', '20210328', '20210329']
    df_result['operating_reserve(MW)'] = pred
    df_result.to_csv(args.output, index=0)