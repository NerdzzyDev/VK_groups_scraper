import asyncio
import aiohttp
import time
from db_api.commands import add_group_user_from_json, count_group_users, get_random_token
from loguru import logger

from db_api.config import bot


# token = "vk1.a.idNC1bLkCLGf7mcuNYpS9PAj94aeZS5C6n6H0oj8vdaRpoyfoMnR2kzrE8Mcr8r5rj7YPLbHn0RlqovLPtZbprHYoKhK2vooggqj5lC9HtHCJEk0UV-PaMGPWTFunwDvxvAqFPqfb1V-oSjF8RBzIxZ-k-94p_9CSbVauYGKIu87avvrrPxU10ouos3zKDYx"
# token = "vk1.a.-YgoyTfIuse34uuCBMjMFipwe3TJolwMWWniyniUq2qKNL7wAQHUZpRsdS3HxwT9hh6LzkfPze08cZ3y-X1NrhaAy2n8Y7X8RpHWUbuslskkCwPrXxCIV4jwc194wUAQHAc6299DLSFAV-QCox7tAsJ5aIoCicvjQ7mzu1q2rFZNPUIw3HzRfVpVUy9FuI0E"



async def generate_data_idsgroup(start_num):
    """Принимает номер с которого начинать диапозон и вовзращает код для выполнения запроса"""
    num_elements = 500
    request_str = 'return ['

    for i in range(25):
        # Создаем новую строку и добавляем в нее числа от i*num_elements+1 до (i+1)*num_elements
        new_string = ','.join(str(j) for j in range(start_num + i * num_elements, start_num + (i + 1) * num_elements))

        request_str+='API.groups.getById({{group_ids: "{ids}", fields: "id,name,contacts", v: "5.131"}}),'.format(ids=new_string)

    request_str += '];'

    return request_str

async def send_telegram_notification(count, error_list):

    text = f"Статус парсинга групп VK:\n\n" \
           f"Всего собранно:\n" \
           f"<code>{count}</code>  / 220000000\n\n" \
           f"Не удалось собрать: {error_list}"

    await bot.send_message(chat_id=-935547037, text=text)

async def fetch(session, url, data):
    await asyncio.sleep(30)
    async with session.post(url, data=data, timeout=100) as response:
        return await response.json()


async def get_groups_async(start_num, request_count):
    iterator = start_num
    ended_with_err = []
    semaphore = asyncio.Semaphore(1)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(request_count): # сколько запросов отправим
            token = await get_random_token()
            code = await generate_data_idsgroup(iterator)
            logger.info(f'Processing a request with groups: {iterator}')
            params = {
                'code': f'{code}',
                'fields': "id, name,contacts",
                'access_token': token,
                'v': '5.131'
            }
            url = "https://api.vk.com/method/execute"
            async with semaphore:
                task = asyncio.create_task(fetch(session, url, data=params))
                tasks.append(task)
            iterator+=12500
            if (i + 1) % 10 == 0:
                count = await count_group_users()
                await send_telegram_notification(count=count,error_list=ended_with_err)
        for response_data in await asyncio.gather(*tasks):
            ended_with_err += await add_group_user_from_json(response_data, iterator)
            count = await count_group_users()
            logger.info(f'Total number of records in group_user table: {count}')
    logger.info(f'Next start_num is: {iterator}')
    with open('ended_with_err.txt', 'w') as f:
        unique_list = list(set(ended_with_err))
        err_list = sorted(unique_list)
        for item in err_list:
            f.write("%s\n" % item)



if __name__ == '__main__':
    # 5112500
    start_time = time.time()
    # asyncio.run(get_groups_async(start_num=5112500, request_count=1))
    asyncio.run(send_telegram_notification())
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения функции: {elapsed_time} секунд")




