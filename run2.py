import pandas as pd
import streamlit as st
import os

# 设置页面标题
st.title("班级排名分析")

# 自动读取当前目录下所有的xlsx文件
file_list = [f for f in os.listdir() if f.endswith('.xlsx')]

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

        # 构建每个班级的信息表格
        table_data = []

        for index, row in date_data.iterrows():
            # 获取该班级的总人数（只在该日期和班级下）
            total_students = len(df_filtered[(df_filtered['授课班级'] == row['授课班级']) & (df_filtered['时间'] == date)])

            # 计算该班级的出勤人数
            present_students = row['出勤状态']

            # 计算出勤率
            attendance_rate = (present_students / total_students) * 100

            # 查找缺勤学生
            absent_students = df_filtered[(df_filtered['授课班级'] == row['授课班级']) & 
                                          (df_filtered['时间'] == date) & 
                                          (df_filtered['出勤状态'] == '缺勤')]

            absent_names = absent_students['姓名'].tolist()
            absent_names_str = ", ".join(absent_names) if absent_names else "没有缺勤学生"

            # 将每个班级的信息添加到表格数据
            table_data.append({
                "班级": row['授课班级'],
                "总人数": total_students,
                "出勤人数": present_students,
                "出勤率": f"{attendance_rate:.2f}%",
                "缺勤学生": absent_names_str
            })

        # 显示表格
        st.subheader(f"班级排名 - {date}")
        st.table(table_data)

else:
    st.error("当前目录下没有找到任何xlsx文件。")
