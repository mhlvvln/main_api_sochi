from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import inspect, select, Column, Integer, TIMESTAMP, Boolean, func

from database.database import Base, async_session


class AbstractModel(Base):
    __abstract__ = True
    hidden = []

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    disabled = Column(Boolean, default=False)

    async def to_dict(self, **kwargs):
        data = {column.key: getattr(self, column.key)
                for column in inspect(self).mapper.column_attrs}
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()

        # for attr, obj in kwargs.items():
        #     if hasattr(self, attr):
        #         print("\n\n\n\n", type(self), getattr(self, attr))
        #         data[attr] = await getattr(self, attr).to_dict(**kwargs)

        for attr, obj in kwargs.items():
            if hasattr(self, attr):
                try:
                    if isinstance(getattr(self, attr), list):
                        data[attr] = [await item.to_dict(**kwargs) for item in getattr(self, attr)]
                    else:
                        data[attr] = await getattr(self, attr).to_dict(**kwargs)
                except AttributeError as e:
                    raise HTTPException(403, "Неожиданная ошибка, связь не уловили")

        for attr in self.hidden:
            data.pop(attr)

        return data

    @classmethod
    async def create_from_dict(cls, data):
        instance = cls(**data)
        async with async_session() as session:
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance.to_dict()

    @classmethod
    async def sort_method(cls, sort_order):
        sort_method = cls.id.asc() if sort_order == "asc" else cls.id.desc()
        return sort_method

    @classmethod
    async def getAll(cls, sort: str = "desc", **kwargs):
        async with async_session() as session:
            instances = await session.execute(select(cls).order_by(await cls.sort_method(sort)))
            results = instances.fetchall()
            return [await result[0].to_dict(**kwargs) for result in results]

    # @classmethod
    # async def getById(cls, id: int, **kwargs):
    #     async with async_session() as session:
    #         instance = await session.execute(select(cls).where(cls.id == id).limit(1))
    #         result = instance.scalar_one_or_none()
    #         if result is None:
    #             raise HTTPException(404, "Не найдено ничего по этому id")
    #         return await result.to_dict(**kwargs)

    @classmethod
    async def getById(cls, id: int, **kwargs):
        async with async_session() as session:
            result = await cls._get_instance_by_id(session, cls, id)
            return await result.to_dict(**kwargs)

    @classmethod
    async def getByUserId(cls, user_id: int, **kwargs):
        async with async_session() as session:
            result = await cls._get_instance_by_id(session, cls, user_id, column_name="user_id")
            return await result.to_dict(**kwargs)

    @staticmethod
    async def _get_instance_by_id(session, model_cls, id, column_name="id"):
        instance = await session.execute(select(model_cls).where(getattr(model_cls, column_name) == id).limit(1))
        result = instance.scalar_one_or_none()
        if result is None:
            raise HTTPException(404, "Не найдено ничего по этому id")
        return result

# пример вызова to_dict:
# user_data = await user.to_dict(organization=True, owner=False, some_other_attr=True)