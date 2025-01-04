import pandas as pd
import streamlit as st
import os

# 设置页面标题
st.title("出勤分析")

# 自动读取当前目录下所有的xlsx文件
file_list = [f for f in os.listdir() if f.endswith('.xlsx')]

# 初始化 session_state
if 'show_ranking' not in st.session_state:
    st.session_state.show_ranking = False

if 'show_filters' not in st.session_state:
    st.session_state.show_filters = True

if file_list:
    # 确保文件名为出勤.xlsx
    selected_file = '出勤.xlsx'  # 假设文件名为出勤.xlsx
    
    # 读取数据
    df = pd.read_excel(selected_file)

    # 清理列名，去除可能的空格
    df.columns = df.columns.str.strip()

    # 处理缺失值：将空字符串替换为 NaN
    df.replace('', pd.NA, inplace=True)

    # 用默认日期填充空值（2000年1月1日），可以防止 NaT 错误
    df['时间'] = df['时间'].fillna(pd.to_datetime('2000-01-01'))

    # 提取筛选条件的独特值，并去重（移除 NaN）
    times = df['时间'].dropna().unique()

    # 左侧栏位设置为筛选器
    with st.sidebar:
        st.header("筛选条件")

        selected_time = st.selectbox("选择时间:", ["全部"] + list(times))

        # 添加班级排名按钮
        show_ranking = st.button("班级排名")

    # 处理按钮点击
    if show_ranking:
        # 切换到班级排名显示
        st.session_state.show_ranking = True
        st.session_state.show_filters = False
    else:
        # 默认显示筛选器
        st.session_state.show_ranking = False
        st.session_state.show_filters = True

    if st.session_state.show_filters:
        # 根据选择的时间进行过滤
        if selected_time != "全部":
            df = df[df['时间'] == selected_time]

        # 显示数据预览
        st.write("数据预览:")
        st.dataframe(df)

    # 如果点击了“班级排名”按钮，显示班级排名柱形图
    if st.session_state.show_ranking:
        # 将签到状态“已签”和“教师代签”视为出勤，其他为缺勤
        df['出勤状态'] = df['签到状态'].apply(lambda x: '出勤' if x in ['已签', '教师代签'] else '缺勤')

        # 只考虑不是2000-01-01的时间
        df_filtered = df[df['时间'] != pd.to_datetime('2000-01-01')]

        # 按日期和授课班级进行分组，并计算每个授课班级的出勤人数
        attendance_by_class_date = df_filtered.groupby(['时间', '授课班级'])['出勤状态'].apply(lambda x: (x == '出勤').sum()).reset_index()

        # 对每个日期进行排序，计算每个班级的出勤排名
        attendance_by_class_date['排名'] = attendance_by_class_date.groupby('时间')['出勤状态'].rank(ascending=False, method='min')

        # 如果选择了特定的时间
        if selected_time != "全部":
            attendance_by_class_date = attendance_by_class_date[attendance_by_class_date['时间'] == pd.to_datetime(selected_time)]

        # 使用st.bar_chart显示柱形图
        st.subheader(f"班级排名 - {selected_time}")
        st.bar_chart(attendance_by_class_date.set_index('授课班级')['出勤状态'])

        # 显示每个班级的出勤数据
        for index, row in attendance_by_class_date.iterrows():
            # 获取该班级的总人数（只在该日期和班级下）
            total_students = len(df_filtered[(df_filtered['授课班级'] == row['授课班级']) & (df_filtered['时间'] == row['时间'])])

            # 计算该班级的出勤人数
            present_students = row['出勤状态']

            # 计算出勤率
            attendance_rate = (present_students / total_students) * 100

            # 显示相关信息
            st.write(f"班级: {row['授课班级']}")
            st.write(f"总人数: {total_students}")
            st.write(f"出勤人数: {present_students}")
            st.write(f"出勤率: {attendance_rate:.2f}%")

            # 显示缺勤学生姓名
            absent_students = df_filtered[(df_filtered['授课班级'] == row['授课班级']) & 
                                          (df_filtered['时间'] == row['时间']) & 
                                          (df_filtered['出勤状态'] == '缺勤')]

            if not absent_students.empty:
                absent_names = absent_students['姓名'].tolist()
                st.write("缺勤学生: " + ", ".join(absent_names))
            else:
                st.write("没有缺勤学生。")

            st.write("---")

else:
    st.error("当前目录下没有找到任何xlsx文件。")
