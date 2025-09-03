import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="需求数量计算工具", page_icon="📊", layout="wide")

st.title("📊 需求数量计算工具")
st.write("上传一个 CSV 文件，自动计算门店需求数量并导出 Excel 文件。")

# 上传 CSV 文件
uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])

# 向上取整到中包装倍数
def adjust_to_pack(value, pack):
    if pack <= 0:
        return value
    multiplier = np.ceil(value / pack)
    return int(multiplier * pack)

if uploaded_file is not None:
    # 读取数据，固定 UTF-8 编码
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except Exception as e:
        st.error(f"文件读取失败，请确认文件是 UTF-8 编码：{e}")
        st.stop()

    # 校验必要字段
    required_cols = ['销售数量', '门店库存', '中包装数', '商品编码']
    if not all(col in df.columns for col in required_cols):
        st.error(f"缺少必要字段，请检查文件是否包含以下列: {', '.join(required_cols)}")
    else:
        # 筛选销售数量不为0的行
        df_filtered = df[df['销售数量'] != 0].reset_index(drop=True)

        # 计算基础需求
        base_demand = df_filtered['销售数量'] * 1 / 2 - df_filtered['门店库存']

        # 计算需求数量
        df_filtered['需求数量'] = np.where(
            df_filtered['销售数量'] > df_filtered['门店库存'],
            [adjust_to_pack(v, p) for v, p in zip(base_demand, df_filtered['中包装数'])],
            0
        )

        # 筛选需求数量大于0的数据
        df_output = df_filtered[df_filtered['需求数量'] > 0][['商品编码', '需求数量']]

        # 显示结果
        st.subheader("📋 计算结果预览")
        st.dataframe(df_output)

        # 将结果导出为 Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_output.to_excel(writer, sheet_name='需求数量', index=False)
        output.seek(0)

        # 提供下载按钮
        st.download_button(
            label="📥 下载结果 Excel 文件",
            data=output,
            file_name="需求数量计算结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("请上传一个包含 `销售数量`、`门店库存`、`中包装数` 和 `商品编码` 的 CSV 文件进行计算。")
