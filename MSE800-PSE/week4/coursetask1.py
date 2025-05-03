file_path = 'sample_text.txt'

with open(file_path, 'r') as file:
    content = file.read()
count = content.count('__')
print(content)
print(f"The number of '__' is: {count}")
