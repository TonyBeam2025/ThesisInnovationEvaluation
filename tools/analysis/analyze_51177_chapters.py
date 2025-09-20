import json

with open('51177_b6ac1c475108811bd4a31a6ebcd397df_toc.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
chapters = []
special = []

for entry in data['entries']:
    if entry['section_type'] == 'traditional_chapter':
        chapters.append(f"{entry['number']} {entry['title']}")
    elif entry['section_type'] in ['abstract', 'references']:
        special.append(f"{entry['section_type']}: {entry['title']}")

print('=== 正文章节 ===')
for i, ch in enumerate(chapters, 1):
    print(f'{i}. {ch}')
    
print('\n=== 特殊章节 ===') 
for i, sp in enumerate(special, 1):
    print(f'{i}. {sp}')
    
print(f'\n总计: {len(chapters)}个正文章节, {len(special)}个特殊章节')
