import asyncio
import aiohttp
import time
from db_api.commands import add_group_user_from_json, count_group_users
from loguru import logger
token = "vk1.a.idNC1bLkCLGf7mcuNYpS9PAj94aeZS5C6n6H0oj8vdaRpoyfoMnR2kzrE8Mcr8r5rj7YPLbHn0RlqovLPtZbprHYoKhK2vooggqj5lC9HtHCJEk0UV-PaMGPWTFunwDvxvAqFPqfb1V-oSjF8RBzIxZ-k-94p_9CSbVauYGKIu87avvrrPxU10ouos3zKDYx"



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
async def fetch(session, url, data):
    await asyncio.sleep(30)
    async with session.post(url, data=data, timeout=100) as response:
        return await response.json()


async def get_groups_async(start_num, request_count):
    iterator = start_num
    ended_with_err = []
    semaphore = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(request_count): # сколько запросов отправим
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
    # 2000000
    start_time = time.time()
    asyncio.run(get_groups_async(start_num=5000000, request_count=8))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Время выполнения функции: {elapsed_time} секунд")




