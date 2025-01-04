import pandas as pd
import streamlit as st
import os

# 设置页面标题
st.title("学生考勤分析")

# 自动读取当前目录下所有的xlsx文件
file_list = [f for f in os.listdir() if f.endswith('.xlsx')]

if file_list:
    # 列出上传的文件供用户选择
    selected_file = st.selectbox("请选择考勤文件:", file_list)

    # 读取选择的文件
    df = pd.read_excel(selected_file)

    # 显示数据表格
    st.write("数据预览:")
    st.dataframe(df)

    # 确保列名正确，避免中文空格问题
    df.columns = df.columns.str.strip()

    # 提取教师和班级列
    teachers = df['教师'].unique()
    classes = df['班级'].unique()
    students = df['学生'].unique()

    # 选择教师
    selected_teacher = st.selectbox("选择教师:", ["全部"] + list(teachers))

    # 根据选择的教师过滤班级
    if selected_teacher != "全部":
        filtered_classes = df[df['教师'] == selected_teacher]['班级'].unique()
    else:
        filtered_classes = classes

    # 选择班级
    selected_class = st.selectbox("选择班级:", ["全部"] + list(filtered_classes))

    # 选择特定的日期列
    date_columns = [col for col in df.columns if col.startswith('日期')]
    selected_date = st.selectbox("选择日期:", date_columns)

    # 根据选择的教师和班级进行过滤
    if selected_teacher != "全部":
        df = df[df['教师'] == selected_teacher]
    if selected_class != "全部":
        df = df[df['班级'] == selected_class]

    # -------------------------------
    # 统计功能
    # -------------------------------

    # 1. 全部学生在特定日期的出勤情况
    total_attendance = df[selected_date].value_counts().to_dict()
    st.subheader(f"全部学生在 {selected_date} 的出勤情况:")
    st.write(total_attendance)

    # 2. 每个班级的出勤情况
    if selected_class == "全部":
        st.subheader(f"各班级在 {selected_date} 的出勤情况:")
        class_attendance = df.groupby('班级')[selected_date].value_counts().unstack(fill_value=0)
        st.dataframe(class_attendance)

    # 3. 每个教师的出勤情况
    if selected_teacher == "全部":
        st.subheader(f"各教师在 {selected_date} 的出勤情况:")
        teacher_attendance = df.groupby('教师')[selected_date].value_counts().unstack(fill_value=0)
        st.dataframe(teacher_attendance)

    # 4. 查询指定学生在所有日期的出勤情况
    selected_student = st.selectbox("查询学生:", students)
    if selected_student:
        student_attendance = df[df['学生'] == selected_student].iloc[0, 3:].to_dict()  # 从日期列开始
        st.subheader(f"{selected_student} 的所有日期出勤情况:")
        st.write(student_attendance)

    st.success("考勤统计完成！")

else:
    st.error("当前目录下没有找到任何xlsx文件。")
