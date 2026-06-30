with open('backend/app/nlp_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines, 1):
    if 'age' in line.lower() and not line.strip().startswith('#'):
        print(f'{i}: {line}', end='')
