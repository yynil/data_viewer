import streamlit as st

st.set_page_config(layout="wide")
import pandas as pd
import os
import numpy as np
# base_data_dir = '/media/yueyulin/KINGSTON/tmp/view_data'
base_data_dir = os.environ.get('BASE_DATA_DIR')

bge_column_names = ['score','similar_doc', 'original_doc', 'id', 'similar_id']
display_column_names = ['相似度', '过滤文本','保留文本','过滤ID','保留ID']
st.sidebar.markdown('## 本次Wudao数据过滤，阈值最小0.97,设置成0.97过滤会过滤14M条，设置成0.99过滤会过滤12M条，总数据未过滤前59M。此次过滤阈值设置为0.99,最后过滤完数据为47M条。此界面可随机采样查看过滤数据，和保留数据。目前保留原则是一对相似数据，保留更长的那一条。')
similarity_threshold = st.sidebar.number_input('选择相似度阈值', min_value=0.97, max_value=1.5, value=0.99, step=0.001, format="%.3f")
sampling_rate = st.sidebar.number_input('选择采样率', min_value=0.001, max_value=0.05, value=0.001, step=0.001, format="%.5f")
search_text = st.sidebar.text_input('输入搜索文本')
# 获取选中目录下的CSV文件
select_file_prob = st.sidebar.number_input('选择文件的概率', min_value=0.005, max_value=0.02, value=0.005, step=0.001, format="%.5f")
csv_files = [f for f in os.listdir(base_data_dir) if f.endswith('.csv') and np.random.rand() < select_file_prob]
# 在侧边栏打印csv文件名
st.sidebar.table(pd.DataFrame(csv_files, columns=['随机选择文件名']))
if csv_files:
    def skip_func(i, p):
        if i == 0:
            return False  # 不跳过第一行（标题行）
        else:
            return np.random.rand() > p  # 以p的概率跳过其他行
    dataframes = [pd.read_csv(os.path.join(base_data_dir, csv_file), skiprows=lambda i: skip_func(i, sampling_rate)) for csv_file in csv_files]
    data = pd.concat(dataframes, ignore_index=True)
    data.drop_duplicates(subset='id', inplace=True)
    data.rename(columns=dict(zip(bge_column_names, display_column_names)), inplace=True)
    # 根据相似度阈值过滤数据
    data = data.loc[data['相似度'] >= similarity_threshold]
    # 过滤文本，保留文本都不能为空
    data.dropna(subset=['过滤文本', '保留文本'], inplace=True)
    # 如果data['保留ID']包含在data['过滤ID']中，则删除那些行
    data = data[~data['保留ID'].isin(data['过滤ID'])]
    # 如果输入了搜索文本，过滤数据
    if search_text:
        data = data[data['过滤文本'].str.contains(search_text) | data['保留文本'].str.contains(search_text)]
        
    # 按照相似度进行排序
    data.sort_values(by='相似度', inplace=True)
    # 调整列的顺序
    data = data.reindex(['相似度', '过滤文本', '保留文本', '过滤ID', '保留ID'], axis=1)
    # 显示当前文件的总条数
    st.sidebar.markdown(f"**总条数：** {len(data)}")

    # 选择每页的条数
    items_per_page = st.sidebar.slider('选择每页条数', 1, 1000, 100)


    num_pages = len(data) // items_per_page
    if len(data) % items_per_page:
        num_pages += 1  # 如果有剩余行数，页数加1
    if num_pages > 1:
        page_num = st.sidebar.slider('选择页数', 1, num_pages)
    else:
        st.sidebar.text('当前页数: 1')
        page_num = 1
    start_index = (page_num - 1) * items_per_page
    end_index = start_index + items_per_page
    end_index = min(end_index, len(data))
    # st.dataframe(data[start_index:end_index])
    # 将数据转换为HTML表格，隐藏索引
    # html = data[start_index:end_index].to_html(index=False)
    # 如果索引已经成为了一列，删除它
    html = data[start_index:end_index].style.set_table_styles(
    [dict(selector='th:nth-child(1)', props=[('width', '1%')]),
     dict(selector='th:nth-child(2)', props=[('width', '9%')]),
     dict(selector='th:nth-child(3)', props=[('width', '40%')]),
     dict(selector='th:nth-child(4)', props=[('width', '40%')]),
     dict(selector='th:nth-child(5)', props=[('width', '5%')]),
     dict(selector='th:nth-child(6)', props=[('width', '5%')])]).to_html(index=False)
    # 使用st.markdown函数来显示HTML表格
    if search_text:
        #replace search_text with red color in markdown in html string
        html = html.replace(search_text, f"<span style='color:red'>{search_text}</span>")
    st.markdown(html, unsafe_allow_html=True)