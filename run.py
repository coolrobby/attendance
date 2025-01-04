import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

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

    # 去除含有空值的行，防止筛选错误
    df = df.dropna(subset=['院系', '专业', '行政班级', '时间', '课程', '授课班级', '教师', '签到状态'])

    # 提取筛选条件的独特值，并去重
    departments = df['院系'].unique()
    majors = df['专业'].unique()
    classes = df['行政班级'].unique()
    times = df['时间'].unique()
    courses = df['课程'].unique()
    taught_classes = df['授课班级'].unique()
    teachers = df['教师'].unique()

    # 左侧栏位设置为筛选器
    with st.sidebar:
        st.header("筛选条件")

        selected_department = st.selectbox("选择院系:", ["全部"] + list(departments))
        selected_major = st.selectbox("选择专业:", ["全部"] + list(majors))
        selected_class = st.selectbox("选择行政班级:", ["全部"] + list(classes))
        selected_time = st.selectbox("选择时间:", ["全部"] + list(times))
        selected_course = st.selectbox("选择课程:", ["全部"] + list(courses))
        selected_taught_class = st.selectbox("选择授课班级:", ["全部"] + list(taught_classes))
        selected_teacher = st.selectbox("选择教师:", ["全部"] + list(teachers))

        # 添加班级分析按钮
        show_ranking = st.button("班级分析")

    # 处理按钮点击
    if show_ranking:
        # 切换到班级分析显示
        st.session_state.show_ranking = True
        st.session_state.show_filters = False
    else:
        # 默认显示筛选器
        st.session_state.show_ranking = False
        st.session_state.show_filters = True

    if st.session_state.show_filters:
        # 根据选择的筛选条件进行过滤
        if selected_department != "全部":
            df = df[df['院系'] == selected_department]
        if selected_major != "全部":
            df = df[df['专业'] == selected_major]
        if selected_class != "全部":
            df = df[df['行政班级'] == selected_class]
        if selected_time != "全部":
            df = df[df['时间'] == selected_time]
        if selected_course != "全部":
            df = df[df['课程'] == selected_course]
        if selected_taught_class != "全部":
            df = df[df['授课班级'] == selected_taught_class]
        if selected_teacher != "全部":
            df = df[df['教师'] == selected_teacher]

        # 显示数据预览
        st.write("数据预览:")
        st.dataframe(df)

    # 如果点击了“班级分析”按钮，显示班级排名柱形图
    if st.session_state.show_ranking:
        # 将签到状态“已签”和“教师代签”视为出勤，其他为缺勤
        df['出勤状态'] = df['签到状态'].apply(lambda x: '出勤' if x in ['已签', '教师代签'] else '缺勤')

        # 按日期和授课班级进行分组，并计算每个授课班级的出勤人数
        attendance_by_class_date = df.groupby(['时间', '授课班级'])['出勤状态'].apply(lambda x: (x == '出勤').sum()).reset_index()

        # 对每个日期进行排序，计算每个班级的出勤排名
        attendance_by_class_date['排名'] = attendance_by_class_date.groupby('时间')['出勤状态'].rank(ascending=False, method='min')

        # 获取所有日期的列表
        all_dates = attendance_by_class_date['时间'].unique()

        # 为每个日期显示排名
        for date in all_dates:
            date_data = attendance_by_class_date[attendance_by_class_date['时间'] == date]
            date_data = date_data.sort_values(by='出勤状态', ascending=False)

            # 使用matplotlib绘制柱形图
            fig, ax = plt.subplots(figsize=(10, 6))

            # 绘制柱形图
            ax.barh(date_data['授课班级'], date_data['出勤状态'], color='skyblue')

            # 为每个柱形图上的柱子添加文本（显示“总人数”，“出勤人数”，“出勤率”）
            for i, (班级, 出勤人数) in enumerate(zip(date_data['授课班级'], date_data['出勤状态'])):
                total_students = len(df[df['授课班级'] == 班级])
                attendance_rate = (出勤人数 / total_students) * 100
                ax.text(出勤人数 + 0.2, i, f"总人数: {total_students}\n出勤人数: {出勤人数}\n出勤率: {attendance_rate:.2f}%", 
                        va='center', fontsize=10)

            # 设置标题和标签
            ax.set_title(f"班级排名 - {date}", fontsize=14)
            ax.set_xlabel('出勤人数', fontsize=12)
            ax.set_ylabel('授课班级', fontsize=12)

            # 显示图表
            st.pyplot(fig)

else:
    st.error("当前目录下没有找到任何xlsx文件。")
