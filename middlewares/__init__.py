from loader import dp
from .middlewares import AccessControlMiddleware

if __name__ == 'middlewares':
    dp.middleware.setup(AccessControlMiddleware())
