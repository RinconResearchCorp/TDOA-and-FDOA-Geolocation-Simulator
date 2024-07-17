def count_items(filename):
    with open(filename, 'r') as f:
        content = f.read()
        items = content.split(',')
        return len(items)
    
count = count_items('received_samples.txt')
print(f'There are {count} items.')