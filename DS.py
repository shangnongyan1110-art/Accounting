# nasdaq_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Load data
@st.cache_data
def load_data():
    # 确保Excel文件路径正确
    file_path = os.path.join(os.getcwd(), "nasdaq_30_combined_cleaned.xlsx")
    df = pd.read_excel(file_path, sheet_name="Income_Statement")
    
    # 日期转换
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    # 处理负值问题
    df['Total Unusual Items Abs'] = df['Total Unusual Items'].abs()
    
    return df

df = load_data()

# 侧边栏过滤器
st.sidebar.header("Filters")
selected_tickers = st.sidebar.multiselect(
    "Select Tickers",
    options=df['Ticker'].unique(),
    default=['OPTN', 'UONEK']
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=[df['Date'].min(), df['Date'].max()],
    min_value=df['Date'].min(),
    max_value=df['Date'].max()
)

# 数据过滤
filtered_df = df[
    (df['Ticker'].isin(selected_tickers)) &
    (df['Date'] >= date_range[0]) &
    (df['Date'] <= date_range[1])
]

# 主仪表盘
st.title("NASDAQ 30 Financial Dashboard")
st.markdown("### Interactive Analysis of Income Statements")

# 标签页
tab1, tab2, tab3, tab4 = st.tabs([
    "Revenue Analysis", 
    "Profit Metrics", 
    "Expense Breakdown",
    "Advanced Charts"
])

with tab1:
    st.header("Revenue Trends")
    
    # 时间序列折线图
    fig1 = px.line(
        filtered_df,
        x="Date",
        y="Total Revenue",
        color="Ticker",
        title="Total Revenue Over Time"
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # 收入构成堆叠柱状图
    fig2 = px.bar(
        filtered_df,
        x="Date",
        y=["Cost Of Revenue", "Gross Profit"],
        color="Ticker",
        barmode="group",
        title="Revenue Composition"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Profitability Analysis")
    
    # 散点矩阵图
    fig3 = px.scatter_matrix(
        filtered_df,
        dimensions=["EBITDA", "Net Income", "Operating Income"],
        color="Ticker",
        title="Profit Metrics Correlation"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # 瀑布图
    if not filtered_df.empty:
        latest_data = filtered_df.groupby('Ticker').last().reset_index()
        fig4 = go.Figure(go.Waterfall(
            name="Profit Breakdown",
            x=latest_data['Ticker'],
            measure=["relative", "relative", "total"],
            y=latest_data[["Gross Profit", "Operating Income", "Net Income"]].values.T,
            connector={"line":{"color":"rgb(63, 63, 63)"}},
        ))
        fig4.update_layout(title="Profit Waterfall by Company")
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.header("Expense Analysis")
    
    # 热力图
    expense_cols = ["Research And Development", 
                   "Selling General And Administration",
                   "Interest Expense"]
    
    fig5 = px.imshow(
        filtered_df[expense_cols].corr(),
        labels=dict(x="Expense Type", y="Expense Type"),
        title="Expense Correlation Heatmap"
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    # 饼图
    selected_ticker = st.selectbox("Select Company for Expense Breakdown:", selected_tickers)
    ticker_data = filtered_df[filtered_df['Ticker'] == selected_ticker].iloc[-1]
    fig6 = px.pie(
        names=expense_cols,
        values=ticker_data[expense_cols],
        title=f"Expense Breakdown for {selected_ticker}"
    )
    st.plotly_chart(fig6, use_container_width=True)

with tab4:
    st.header("Advanced Visualizations")
    
    # 3D散点图
    fig7 = px.scatter_3d(
        filtered_df,
        x="Total Revenue",
        y="Net Income",
        z="EBITDA",
        color="Ticker",
        size="Total Expenses",
        title="3D Financial Health View"
    )
    st.plotly_chart(fig7, use_container_width=True)
    
    # 动态气泡图（已修复）
    fig8 = px.scatter(
        filtered_df,
        x="Tax Rate For Calcs",
        y="Normalized EBITDA",
        size="Total Unusual Items Abs",  # 使用绝对值列
        color="Ticker",
        animation_frame="Date",
        range_x=[0, 0.5],
        range_y=[-1e7, 1e7],
        title="Tax Efficiency vs Profitability Over Time (Absolute Values)",
        size_max=50  # 控制气泡最大尺寸
    )
    st.plotly_chart(fig8, use_container_width=True)

# 数据表格显示
st.divider()
st.subheader("Raw Data Preview")
st.dataframe(filtered_df.sort_values("Date", ascending=False), height=300)

# 添加数据统计摘要
st.sidebar.divider()
st.sidebar.subheader("Data Summary")
st.sidebar.write(f"Total Companies: {len(df['Ticker'].unique())}")
st.sidebar.write(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
st.sidebar.write(f"Current Selection: {len(filtered_df)} rows")