import asyncio
import asyncpg
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, func
from sqlalchemy.sql.expression import select
from sqlalchemy.schema import DropTable, CreateTable
from sqlalchemy.ext.declarative import DeferredReflection
from db_api.config import Base, async_session, async_engine
from db_api.models.user import User, Group, GroupUser, Vk_tokens



async def add_group_user_from_json(row_json, iterator):
    async with AsyncSession(async_engine) as session:
        err = []
        try:
            async with session.begin():
                for groups in row_json["response"]:
                    for group in groups:
                        group_id = group["id"]
                        group_name = group.get("name", None)

                        # Проверяем, существует ли группа в базе данных
                        existing_group = await session.execute(select(Group).where(Group.id == group_id))
                        existing_group = existing_group.scalar_one_or_none()
                        if existing_group is None:
                            # Если группы нет в базе данных, создаем новую
                            new_group = Group(id=group_id, name=group_name)
                            session.add(new_group)
                        else:
                            # Если группа уже существует, используем ее
                            new_group = existing_group

                        contacts = group.get("contacts", [])
                        for contact in contacts:
                            user_id = contact.get("user_id")

                            # Проверяем, существует ли пользователь в базе данных
                            existing_user = await session.execute(select(User).where(User.id == user_id))
                            existing_user = existing_user.scalar_one_or_none()
                            if existing_user is None:
                                if user_id is None:
                                    pass
                                else:
                                    # Создаем нового пользователя
                                    new_user = User(id=user_id, phone=contact.get("phone"), email=contact.get("email"), desc=contact.get("desc"))
                                    session.add(new_user)
                                    # Получаем созданного пользователя из базы данных
                                    user = new_user
                            else:
                                user = existing_user

                            # Проверяем, существует ли связь между группой и пользователем
                            group_user = await session.execute(select(GroupUser).where(GroupUser.group_id == group_id, GroupUser.user_id == user_id))
                            group_user = group_user.scalar_one_or_none()
                            if group_user is None:
                                # Проверяем, существует ли пользователь вообще
                                if existing_user is not None:
                                    # Создаем связь между группой и пользователем
                                    new_group_user = GroupUser(group_id=group_id, user_id=user_id)
                                    session.add(new_group_user)

                await session.commit()
        except KeyError:
            logger.error(f'Error! iterator: {iterator} | error_code: {row_json["error"]["error_code"]} | error_msg: {row_json["error"]["error_msg"]}')
            err.append(iterator)
            logger.error(f'Error list: {err}')

        return err



async def get_user_groups(user_id):
    async with AsyncSession(async_engine) as session:
        stmt = select(GroupUser.group_id).where(GroupUser.user_id == user_id)
        result = await session.execute(stmt)
        group_ids = [row[0] for row in result]
        return group_ids


async def count_group_users():
    async with AsyncSession(async_engine) as session:
        count = await session.execute(select(func.count(GroupUser.group_id)))
        return count.scalar()


async def create_tables():

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_all_tables():
    async with async_session() as session:

        # # Отражение всех таблиц базы данных
        # await Base.metadata.create_all(async_engine)

        # Отключение автоматической фиксации изменений
        async with session.begin():
            # Удаление всех таблиц
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(DropTable(table))

        # Фиксация изменений
        await session.commit()

############### TOKENS #################

async def add_token_to_database(token):
    async with AsyncSession(async_engine) as session:
        # Создание нового экземпляра класса Vk_tokens
        new_token = Vk_tokens(token=token, status='active')

        # Добавление нового токена в базу данных
        session.add(new_token)
        await session.commit()

    # Закрытие соединения
    await async_engine.dispose()

async def get_random_token():
    async with AsyncSession(async_engine) as session:
        # Получение случайного токена из базы данных
        random_token = await session.execute(select(Vk_tokens.token).order_by(func.random()))
        return random_token.scalar_one()
    await async_engine.dispose()






if __name__ == '__main__':
    asyncio.run(create_tables())
