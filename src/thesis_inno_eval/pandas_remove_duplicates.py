import os
import json
import pandas as pd

def pandas_remove_duplicates(input_file, output_file):
    # 读取JSON文件到DataFrame
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # 处理缺失PublicationYear字段
    if 'PublicationYear' not in df.columns:
        df['PublicationYear'] = ''
    else:
        df['PublicationYear'] = df['PublicationYear'].fillna('')

    # 创建组合键用于去重
    df['combined_key'] = df['Title'].str.lower().str.strip() + '|' + df['PublicationYear'].astype(str)
    
    # 去重
    df_unique = df.drop_duplicates(subset=['combined_key'])
    df_unique = df_unique.drop(columns=['combined_key'])
    
    # 转换回JSON格式
    unique_entries = df_unique.to_dict('records')
    
    # 如果output_file存在，先删除
    if os.path.exists(output_file):
        os.remove(output_file)

    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_entries, f, ensure_ascii=False, indent=4)

# 不要在模块顶层直接调用函数