import asyncio

from db_api.commands import add_token_to_database, get_random_token

if __name__ == '__main__':
    # asyncio.run(add_token_to_database(token="vk1.a.-YgoyTfIuse34uuCBMjMFipwe3TJolwMWWniyniUq2qKNL7wAQHUZpRsdS3HxwT9hh6LzkfPze08cZ3y-X1NrhaAy2n8Y7X8RpHWUbuslskkCwPrXxCIV4jwc194wUAQHAc6299DLSFAV-QCox7tAsJ5aIoCicvjQ7mzu1q2rFZNPUIw3HzRfVpVUy9FuI0E"))
    token = asyncio.run((get_random_token()))
    print(token)