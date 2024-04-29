import streamlit as st

st.set_page_config(layout="wide")
import pandas as pd
import os
suffix = ["_0.95_0.98.csv","_0.98_1.csv","_0_0.95.csv","_1_1.5.csv"]

# base_data_dir = '/media/yueyulin/KINGSTON/tmp/view_data'
base_data_dir = os.environ.get('BASE_DATA_DIR')
st.sidebar.markdown("两个目录的csv使用不同的embedding模型。一个使用bgem3作编码，一个使用rwkv6+lora编码。两者阈值过滤后结果不一样")
# 选择CSV文件目录
csv_dirs = [f"{base_data_dir}/bgem3", f'{base_data_dir}/rwkv6']  # 
selected_csv_dir = st.sidebar.selectbox("选择CSV文件目录", csv_dirs)

bge_column_names = ['filtered_score','similar_doc', 'original_doc', 'id', 'filtered_by']
rwkv_column_names = ['score','similar_doc',  'original_doc','id', 'similar_id']
display_column_names = ['相似度', '过滤文本','保留文本','过滤ID','保留ID']

similarity_threshold = st.sidebar.number_input('选择相似度阈值', min_value=0.9, max_value=1.5, value=0.95, step=0.001, format="%.3f")
search_text = st.sidebar.text_input('输入搜索文本')
# 获取选中目录下的CSV文件
csv_files = [f for f in os.listdir(selected_csv_dir) if f.endswith('.csv')]
if csv_files:
    dataframes = [pd.read_csv(os.path.join(selected_csv_dir, csv_file)) for csv_file in csv_files]
    data = pd.concat(dataframes, ignore_index=True)
    data.drop_duplicates(subset='id', inplace=True)
    if 'similar_id' in data.columns:
        data.rename(columns=dict(zip(rwkv_column_names, display_column_names)), inplace=True)
    else:
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
    html = data[start_index:end_index].to_html(index=False)
    # 使用st.markdown函数来显示HTML表格
    if search_text:
        #replace search_text with red color in markdown in html string
        html = html.replace(search_text, f"<span style='color:red'>{search_text}</span>")
    st.markdown(html, unsafe_allow_html=True)