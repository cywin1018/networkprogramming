from urllib.parse import urlsplit

u = urlsplit('http://www.google.com:80/search?q=python')
print(u)
print(u.scheme)
print(u.netloc)