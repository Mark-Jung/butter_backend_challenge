from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'FileSystemCache',
    'CACHE_DEFAULT_TIMEOUT': 60,
    'CACHE_DIR': 'cache_dir'
})