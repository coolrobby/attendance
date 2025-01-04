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

    # 用默认日期填充空值（2000年1月1日）
    df['时间'] = df['时间'].fillna(pd.to_datetime('2000-01-01'))

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

        # 显示筛选条件
        st.subheader("当前筛选条件:")
        filter_conditions = []

        if selected_department != "全部":
            filter_conditions.append(f"院系: {selected_department}")
        if selected_major != "全部":
            filter_conditions.append(f"专业: {selected_major}")
        if selected_class != "全部":
            filter_conditions.append(f"行政班级: {selected_class}")
        if selected_time != "全部":
            filter_conditions.append(f"时间: {selected_time}")
        if selected_course != "全部":
            filter_conditions.append(f"课程: {selected_course}")
        if selected_taught_class != "全部":
            filter_conditions.append(f"授课班级: {selected_taught_class}")
        if selected_teacher != "全部":
            filter_conditions.append(f"教师: {selected_teacher}")

        # 如果有筛选条件，显示它们，每个条件独占一行
        if filter_conditions:
            for condition in filter_conditions:
                st.markdown(f"- {condition}")
        else:
            st.write("未选择任何筛选条件。")

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

        # 获取所有日期的列表
        all_dates = attendance_by_class_date['时间'].unique()

        # 为每个日期显示排名
        for date in all_dates:
            date_data = attendance_by_class_date[attendance_by_class_date['时间'] == date]
            date_data = date_data.sort_values(by='出勤状态', ascending=False)

            # 使用st.bar_chart显示柱形图
            st.subheader(f"班级排名 - {date}")
            st.bar_chart(date_data.set_index('授课班级')['出勤状态'])

            # 显示每个班级的出勤数据
            for index, row in date_data.iterrows():
                # 获取该班级的总人数（只在该日期和班级下）
                total_students = len(df_filtered[(df_filtered['授课班级'] == row['授课班级']) & (df_filtered['时间'] == date)])

                # 计算该班级的出勤人数
                present_students = row['出勤状态']

                # 计算出勤率
                attendance_rate = (present_students / total_students) * 100

                # 显示相关信息
                st.write(f"班级: {row['授课班级']}")
                st.write(f"总人数: {total_students}")
                st.write(f"出勤人数: {present_students}")
                st.write(f"出勤率: {attendance_rate:.2f}%")
                st.write("---")

else:
    st.error("当前目录下没有找到任何xlsx文件。")
