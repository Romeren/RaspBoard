
def get_content(filename):
    file = open(filename, 'r')
    content = file.read().replace('\n', '')
    file.close()
    return content
