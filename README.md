最後更新日期: 2021-03-19

以下是我在 jupyter notebook 的分析過程，由於 markdown 的限制，並沒有把所有 output 都記錄在此份 README.md

## 引入函式庫

```python
import pandas as pd

# --- plotly ---
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
import datetime
pio.templates.default = "plotly_dark"
```

## 取得原始資料
- 讀取[台灣電力公司_過去電力供需資訊](https://data.gov.tw/dataset/19995)作為 `df1` 
    - 區間: 2019/01/01 ~ 2021/01/31
    - 包含 “日期”、”尖峰負載(MW)”、”備轉容量(MW)”, “備轉容量率(%)”...
    - ”備轉容量(MW)” (operating reserve) 是預測的目標

- 讀取[台灣電力公司_本年度每日尖峰備轉容量率](https://data.gov.tw/dataset/25850)作為 `df2`
    - 區間: 2020/01/01 ~ 2020/12/25
    - 包含 “日期”、”備轉容量(萬瓩)”、“備轉容量率(%)”
    - 1 萬瓩 = 10 MW

查看 `df1` 的所有欄位

```python
df1 = pd.read_csv('1.csv')
df2 = pd.read_csv('2.csv')
df1.columns
```

其中只關注全局的資訊，把個別發電廠的欄位都捨棄，將`工業用電`和`民生用電`相加儲存到 `總用電(百萬度)` ，並且將日期變為 `datetime`

```python
df1 = df1[['日期', '淨尖峰供電能力(MW)', '尖峰負載(MW)', '備轉容量(MW)', '備轉容量率(%)']]
tmp = []
for i in df1.index:
    tmp.append(datetime.datetime.strptime(str(df1.loc[i, '日期']), '%Y%m%d'))
df1['日期2'] = tmp
df1
```

---

用 plotly 畫出淨尖峰供電能力(MW), 尖峰負載(MW),備轉容量(MW) 的折線圖

```python
fig = px.line(df1, x='日期2', y=['淨尖峰供電能力(MW)', '尖峰負載(MW)','備轉容量(MW)'], title='備轉容量')
fig.update_layout(title='供電、負載、備轉', xaxis_title='日期', yaxis_title='功率 (MW)')
fig.show()
```

![](readme-imgs/0.png)


可以發現 2019 年 4 月份的 `備轉容量(MW)` 的數值很奇怪，跟其他時間相比特別低，這裡我透過 excel 開啟檔案，透過觀察發現:  
>備轉容量(MW) = 淨尖峰供電能力(MW) - 尖峰負載(MW)

---

以下，我們將 `備轉容量(MW)` 重新計算，取代錯誤的值，然後再次觀察圖表

```python
tmp = []
for i in df1.index:
    tmp.append(df1.loc[i, '淨尖峰供電能力(MW)'] - df1.loc[i, '尖峰負載(MW)'])
df1['備轉容量(MW)'] = tmp
fig = px.line(df1, x='日期2', y=['淨尖峰供電能力(MW)', '尖峰負載(MW)','備轉容量(MW)'])
fig.update_layout(title='供電、負載、備轉', xaxis_title='日期', yaxis_title='功率 (MW)')
fig.show()
```

![](readme-imgs/1.png)

- 由上圖可以發現天氣越炎熱用電量越高，但是備載容量增加的沒那麼明顯  
- 供用電呈現密集的震盪，我初步猜測震盪的高峰代表平日，低谷代表假日

---

我在下兩張圖將每個日期用圓點標示，觀察平日和假日用電的差異，並且我只擷取 3 至 4 月觀察，我認為其他月份的 pattern 參考意義不大

```python
# begin day and end day
begin = 59
end = 119

fig = go.Figure()
fig.add_trace(go.Scatter(x=df1['日期2'][begin:end], y=df1['淨尖峰供電能力(MW)'][begin:end], mode='lines+markers', name='淨尖峰供電能力(MW)'))
fig.add_trace(go.Scatter(x=df1['日期2'][begin:end], y=df1['尖峰負載(MW)'][begin:end], mode='lines+markers', name='尖峰負載(MW)'))
fig.add_trace(go.Scatter(x=df1['日期2'][begin:end], y=df1['備轉容量(MW)'][begin:end], mode='lines+markers', name='備轉容量(MW)'))
title_str = '供電用電狀況 (' + str(df1['日期2'][begin]) + ' - ' + str(df1['日期'][end]) + ')'
fig.update_layout(title=title_str, xaxis_title='日期', yaxis_title='功率 (MW)')
fig.show()
```

![](readme-imgs/2.png)

```python
# begin day and end day
begin = 425
end = 485

fig = go.Figure()
fig.add_trace(go.Scatter(x=df1['日期2'][begin:end], y=df1['淨尖峰供電能力(MW)'][begin:end], mode='lines+markers', name='淨尖峰供電能力(MW)'))
fig.add_trace(go.Scatter(x=df1['日期2'][begin:end], y=df1['尖峰負載(MW)'][begin:end], mode='lines+markers', name='尖峰負載(MW)'))
fig.add_trace(go.Scatter(x=df1['日期2'][begin:end], y=df1['備轉容量(MW)'][begin:end], mode='lines+markers', name='備轉容量(MW)'))
title_str = '供電用電狀況 (' + str(df1['日期2'][begin]) + ' - ' + str(df1['日期'][end]) + ')'
fig.update_layout(title=title_str, xaxis_title='日期', yaxis_title='功率 (MW)')
fig.show()
```

![](readme-imgs/3.png)

- 由上圖可以發現震盪的波峰通常都維持 5 天，對照日曆也確定是週一到五，而低谷則是星期六日和國定假日
- 備載容量卻沒有明顯的波峰波谷，而且通常備載容量通常在比前幾日高出許多後又會降回來
- 一樣，備載容量有時在假日時會增加，但沒那麼規律，基本上可以視為與尖峰負載無關

>由此我得出一個結論: 備載容量在假日時有機會微幅提升，但大部分時候是穩定的

---

接下來我新增一個欄位，將資料標記星期一至星期天 (1 ~ 7)

```python
day = 2
tmp = []
for i in df1.index:
    tmp.append(day)
    if day == 7:
        day = 1
    else:
        day = day + 1
df1['星期'] = tmp

day = 5
tmp = []
for i in df2.index:
    tmp.append(day)
    if day == 7:
        day = 1
    else:
        day = day + 1
df2['星期'] = tmp
```

再看看 `df2` (台灣電力公司_本年度每日尖峰備轉容量率) 的資料，先把備轉容量單位換成 MW

```python
df2['備轉容量(MW)'] = df2['備轉容量(萬瓩)'] * 10
tmp = []
for i in df2.index:
    tmp.append(datetime.datetime.strptime(str(df2.loc[i, '日期']), '%Y/%m/%d'))
df2['日期2'] = tmp
df2
```

2/27, 2/28, 2/29 是國定連假，會造成雜訊，故先把這三天 drop 掉

```python
tmp = 0
while True:
    if df2['日期'][tmp] == '2021/02/27':
        break
    else:
        tmp = tmp + 1
df2 = df2.drop([tmp, tmp+1, tmp+2])
df2 = df2.reset_index(drop=True)
```

---

接著我觀察每日往前回推 4、7、14 日的均線

```
def avg_line(n):
    lst = []
    for i in range(n, len(df2)):
        lst.append(sum(df2[i - n:i]['備轉容量(MW)'].tolist()) / n)
    return lst
    
fig = go.Figure()
fig.add_trace(go.Scatter(x=df2['日期2'], y=df2['備轉容量(MW)'], mode='lines+markers', name='備轉容量(MW)'))
#fig.add_trace(go.Scatter(x=df2['日期2'][14:], y=avg_line(14), mode='lines', name = '14 日均線'))
fig.add_trace(go.Scatter(x=df2['日期2'][14:], y=avg_line(14), name='14 日均線', line = dict(dash='dash')))
fig.add_trace(go.Scatter(x=df2['日期2'][7:], y=avg_line(7), name = '7 日均線', line = dict(color='yellow', dash='dash')))
fig.add_trace(go.Scatter(x=df2['日期2'][4:], y=avg_line(4), name = '4 日均線', line = dict(color='green', dash='dash')))
title_str = '備轉容量 2021'
fig.update_layout(title=title_str, xaxis_title='日期', yaxis_title='功率 (MW)')
fig.show()
```

![](readme-imgs/4.png)

觀察 3、5、7 日的 moving averages

```python
def avg_line(n):
    lst = []
    for i in range(n, len(df2)):
        lst.append(sum(df2[i - n:i]['備轉容量(MW)'].tolist()) / n)
    return lst

fig = go.Figure()
fig.add_trace(go.Scatter(x=df2['日期2'], y=df2['備轉容量(MW)'], mode='lines+markers', name='備轉容量(MW)'))
fig.add_trace(go.Scatter(x=df2['日期2'][1:], y=avg_line(3), name='3-period MA', line = dict(dash='dash')))
fig.add_trace(go.Scatter(x=df2['日期2'][2:], y=avg_line(5), name='5-period MA', line = dict(dash='dash')))
fig.add_trace(go.Scatter(x=df2['日期2'][3:], y=avg_line(7), name='7-period MA', line = dict(color='yellow', dash='dash')))
```

![](readme-imgs/5.png)

由均線圖和 moving averages 圖可以發現 moving averages 的趨勢要比前 n 日平均更準，不知道有沒有機會拿這兩樣資訊來預測