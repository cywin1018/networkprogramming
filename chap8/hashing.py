import hashlib
def alpha_shard(word):
    """Do a poor job of assigning data to servers by using first letters."""
    if word[0] < "g":
        return "server0"
    elif word[0] < "n":
        return "server1"
    elif word[0] < "t":
        return "server2"
    else:
        return "server3"
def hash_shard(word):
    """Assign data to servers by hashing the word."""
    return "server%d" % (hash(word) % 4)

def md5_shard(word):
    """Assign data to servers by hashing the word."""
    data = word.encode('utf-8')
    return "server%d" %(hashlib.md5(data).digest()[-1]  % 4)
if __name__ =='__main__':
    words = open('words.txt').read().split()
    for function in alpha_shard, hash_shard,md5_shard:
        d = {'server0': 0, 'server1': 0, 'server2': 0, 'server3': 0}
        for word in words:
            d[function(word.lower())]+=1
        print(function.__name__[:6])
        for key,value in sorted(d.items()):
            print('   {} {} {:.2}'.format(key,value,value/len(words)))
        print()