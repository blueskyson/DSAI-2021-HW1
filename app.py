
import argparse
import pandas as pd

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

def model1(df, begin_date, interval, n):
    tmp = 0
    for i in df.index:
        if df.loc[i, '日期'] == begin_date:
            break
        else:
            tmp = tmp + 1
    lst = df[tmp - n : tmp]['備轉容量(MW)'].tolist()
    ret = []
    mean = sum(lst) / n
    for i in range(0, interval):
        ret.append(int(mean))
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
    df_training['備轉容量(MW)'] = df_training['備轉容量(萬瓩)'] * 10

    # remove 2/27, 2/28, 3/1 from training data
    df_training = remove_228(df_training)

    # predict
    pred = model1(df_training, '2021/03/13', 7, 8)

    # save
    df_result = pd.DataFrame()
    df_result['date'] = ['20210323', '20210324', '20210325', '20210326', '20210327', '20210328', '20210329']
    df_result['operating_reserve(MW)'] = pred
    df_result.to_csv(args.output, index=0)