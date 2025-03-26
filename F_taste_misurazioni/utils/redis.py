from redis import ConnectionPool, Redis

redis_pool = None  # Global variable to store the Redis connection pool

def init_redis_connection_pool(app):
    """
    Initializes the Redis connection pool using the application's configuration.
    This function should be called from your application factory.
    """

    global redis_pool
    redis_pool = ConnectionPool(
        host=app.config.get('REDIS_HOST', 'localhost'), 
        port=app.config.get('REDIS_PORT', 6379), 
        db=0, 
        password=app.config.get('REDIS_PASSWORD', None), 
        decode_responses=True
    )

def get_redis_connection():
    global redis_pool
    return Redis(connection_pool=redis_pool)