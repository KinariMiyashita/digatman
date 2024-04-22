import os
import re
import csv

def replace_footer_content(folder_path, exclude_folders, tag_name, id_name, min_line_count, new_content, base_url, output_csv_path):
  modified_files = []

  # 除外フォルダのパス
  full_exclude_folders = [os.path.normpath(os.path.join(folder_path, folder)) for folder in exclude_folders]
  
  # 正規表現をコンパイル（タグの前のインデントを含める）
  tag_regex = re.compile(r'(\s*)<{}[^>]*id=["\']{}["\'].*?</{}>'.format(tag_name, id_name, tag_name), flags=re.DOTALL)

  for root, dirs, files in os.walk(folder_path):
    for filename in files:
      if filename.endswith('.html'):
        file_path = os.path.join(root, filename)

        # 除外リストに含まれるフォルダのパスが現在のファイルパスに含まれているかチェック
        if any(file_path.startswith(exclude_folder) for exclude_folder in full_exclude_folders):
            continue  

        with open(file_path, 'r', encoding='utf-8') as file:
          original_content = file.read()

        for match in tag_regex.finditer(original_content):
          indent = match.group(1)
          line_count = match.group(0).count('\n') + 1
          if line_count > min_line_count:
            # インデントを保持して新しいコンテンツを挿入
            indented_content = ''.join(indent + line if line.strip() else line for line in new_content.split('\n'))
            new_content_full = original_content[:match.start()] + indented_content + original_content[match.end():]

            with open(file_path, 'w', encoding='utf-8') as file:
              file.write(new_content_full)

            # 修正されたファイルのパスを記録
            relative_path = os.path.relpath(file_path, start=folder_path)
            full_url = os.path.join(base_url, relative_path.replace(os.sep, '/'))
            modified_files.append((relative_path, full_url))

  # CSVファイルに結果を書き出し
  with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['相対パス', 'URL'])
    writer.writerows(modified_files)

# フォルダのパスを指定
folder_path = './example'

# 除外するフォルダ配下のフォルダパス
exclude_folders = ['test/test2']

# タグの種類
tag_name = 'div'

# id名
id_name = 'test_id'

# 置換対象の最低コード行数（置換対象をより正確に判断）
min_line_count = 100

# 置換内容
new_content = '''
<div id='test'>
    test
</div>
'''.strip()

# リンクのベースURL
base_url = 'http://example.com/'

# 変更ファイルとパスをcsvに記録
output_csv_path = 'modified_files.csv'

replace_footer_content(folder_path, exclude_folders, tag_name, id_name, min_line_count, new_content, base_url, output_csv_path)
