def append_slash(url):
    if type(url) != str:
        return url
    if not url.endswith('/'):
        url += '/'
    return url