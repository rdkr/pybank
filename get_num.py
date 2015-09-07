def get_num(x): # http://stackoverflow.com/a/10365472
    return float(''.join(ele for ele in x if ele.isdigit() or ele == '.' or ele == '-'))