import pandas as pd
import streamlit as st
import os

# 设置页面标题
st.title("出勤分析")

# 自动读取当前目录下所有的xlsx文件
file_list = [f for f in os.listdir() if f.endswith('.xlsx')]

if file_list:
    # 确保文件名为出勤.xlsx
    selected_file = '出勤.xlsx'  # 假设文件名为出勤.xlsx
    
    # 读取数据
    df = pd.read_excel(selected_file)

    # 清理列名，去除可能的空格
    df.columns = df.columns.str.strip()

    # 提取筛选条件的独特值
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

    # 统计“签到状态”字段的不同值所占百分比
    if '签到状态' in df.columns:
        attendance_counts = df['签到状态'].value_counts()
        total_count = attendance_counts.sum()
        attendance_percentage = (attendance_counts / total_count) * 100

        # 显示统计结果
        st.subheader("签到状态的百分比统计:")
        
        # 显示总人数
        st.write(f"总人数: {total_count}")

        # 显示各个值的人数和百分比
        for status, count in attendance_counts.items():
            percentage = attendance_percentage[status]
            st.write(f"{status}: {count} 人，占 {percentage:.2f}%")
    else:
        st.error("数据中没有 '签到状态' 字段。")

else:
    st.error("当前目录下没有找到任何xlsx文件。")
