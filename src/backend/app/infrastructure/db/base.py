from sqlalchemy.orm import DeclarativeBase
import datetime

class Base(DeclarativeBase):
    __hidden__fields = ["password_hash"]
    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            if column.name in self.__hidden__fields:
                continue
            
            value = getattr(self, column.name)

            # Convert datetime to ISO string for JSON
            if isinstance(value, datetime.datetime):
                value = value.isoformat()

            result[column.name] = value

        return result