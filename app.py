# from hamcrest import none
import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import pymc3 as pm

plt.style.use('grayscale')
plt.style.use('seaborn-whitegrid')
np.random.seed(0)

st.set_option('deprecation.showPyplotGlobalUse', False)

# ページの既定の設定を構成する
st.set_page_config(page_title="スコアリング",
                   page_icon="👩‍💻",
                   initial_sidebar_state="collapsed",
                   )

# 関数の実行をメモするための関数デコレータ
@st.cache(persist=False,
          allow_output_mutation=True,
          suppress_st_warning=True,
          show_spinner= True)

def load_csv():

    # データを読み込む
    df_input = pd.DataFrame()

    # データを読み込む(CSV)
    df_input = pd.read_csv(input,
                            engine='python', #日本語や全角が入ったファイル読み込み時のエラー解決策
                            encoding='utf-8'
                            )    

    # データを返す
    return df_input

st.title("滞在時間")
st.write("このアプリは、ベイズ統計を用いてWebページの滞在時間（秒）を推定します。")
df = pd.DataFrame()
colors = ['gray', 'black', 'red', 'green', 'blue', 'cyan', 'yellow', 'magenta']

st.subheader('1.データの読み込み')
st.write('CSVファイルをアップロードしてください。')

input = st.file_uploader("Upload CSV", type=".csv")
example_file = ""

use_example_file = st.checkbox(
    "CSVファイル例", False, help="見本ファイルを表示します。"
)

if use_example_file:
    example_file = "sumple_time.csv"

if example_file:
    example_df = pd.read_csv(example_file)
    st.markdown("### 見本ファイル")
    st.dataframe(example_df.head())

if input:
    with st.spinner('データ読み込み中...'):
        df = load_csv()
        output = 0

if st.checkbox("ヒストグラム",key="show"):
    if input:
        with st.spinner("データをプロットする………"):
            # dfの列の数のヒストグラムを作成する
            for col,color in zip(range(len(df.columns)),colors):
                plt.hist(df.iloc[:,col], bins=50, alpha=0.5,color=color,label=df.columns[col])
                plt.legend(loc="upper right", fontsize=13)

            st.pyplot()
        
    if not input:
        st.warning('CSVファイルをアップロードする必要があります。')

st.subheader('2.結果の表示')
if st.checkbox("算出",key="cal1"):

    if input:
        st.write('Aから順番に表示されます。')
        st.write('右側のグラフの形が、複数の帯のようになっていることを確認してください。なっていない場合は、正しく分析できていません。')
        for col in range(len(df.columns)):
            with pm.Model() as model:
                theta = pm.Uniform('theta', lower=0, upper=3000)
                obs = pm.Exponential('obs', lam=1/theta, observed=df.iloc[:,col])
                trace = pm.sample(5000, chains=2)
                pm.plot_trace(trace)
                st.write(df.columns[col])
                st.pyplot()
                pm.plot_posterior(trace, hdi_prob=0.95)
                st.pyplot()
        
    if not input:
        st.warning('CSVファイルをアップロードする必要があります。')
