from sqlalchemy import Column, Integer, String, BIGINT, DateTime, func, ForeignKey, Boolean, Index
from sqlalchemy.orm import declarative_base, relationship

from Database.MySqlFunc import utcnow

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, autoincrement=True, primary_key=True)
    telegram_id = Column(BIGINT, unique=True, nullable=True)
    telegram_username = Column(String, nullable=True)
    telegram_fullname = Column(String, server_default="Unknown")
    is_blocked = Column(Boolean, server_default=func.cast(False, Boolean))
    Khatma_List = relationship("Khatma", back_populates="User")
    Khatmas_Done_List = relationship("Khatma_Done", back_populates="User")
    Khatma_Parts_List = relationship("Khatma_Parts", back_populates="User")
    Khatma_Parts_Done_List = relationship("Khatma_Parts_Done", back_populates="User")

    def __repr__(self):
        return f"User{self.telegram_id, self.telegram_fullname}"


class Khatma(Base):
    __tablename__ = 'Khatma'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(ForeignKey("User.telegram_id"), nullable=False)
    name_of_opener = Column(String)
    time = Column(DateTime(timezone=False), server_default=utcnow())
    max_number_of_booked_parts_by_person = Column(Integer)
    description = Column(String)
    is_private = Column(Boolean)
    number_of_days_to_finish_a_part = Column(Integer)

    # relations
    Khatma_Parts_List = relationship("Khatma_Parts", back_populates="Khatma")
    User = relationship("User", back_populates="Khatma_List")

    def __repr__(self):
        return f"{self.id, self.name_of_opener}"


class Khatma_Done(Base):
    __tablename__ = 'Khatma_Done'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("User.telegram_id"), nullable=False)
    name_of_opener = Column(String)
    description = Column(String)
    start_date = Column(DateTime(timezone=False))
    end_date = Column(DateTime(timezone=False))
    is_canceled = Column(Boolean, server_default=func.cast(False, Boolean))

    # relations
    User = relationship("User", back_populates="Khatmas_Done_List")
    Khatma_Parts_List = relationship("Khatma_Parts_Done", back_populates="Khatma_Done")

    def __repr__(self):
        return f"{self.id, self.name_of_opener}"


class Khatma_Parts(Base):
    __tablename__ = 'Khatma_Parts'
    part_id = Column(Integer, autoincrement=True, primary_key=True)
    khatma_id = Column(ForeignKey("Khatma.id"), nullable=False, index=True)
    part_no = Column(Integer, index=True)
    user_id = Column(ForeignKey("User.telegram_id"), nullable=True)
    part_state = Column(Integer)
    part_start = Column(DateTime(timezone=False))
    part_end = Column(DateTime(timezone=False))
    part_deadline = Column(DateTime(timezone=False))
    part_next_notification_time = Column(DateTime(timezone=False))
    # relations
    User = relationship('User', back_populates='Khatma_Parts_List')
    Khatma = relationship('Khatma', back_populates='Khatma_Parts_List', lazy="immediate")
    __table_args__ = (Index('my_index', "khatma_id", "part_no"),)


class Khatma_Parts_Done(Base):
    __tablename__ = 'Khatma_Parts_Done'
    part_id = Column(Integer, primary_key=True)
    khatma_id = Column(ForeignKey("Khatma_Done.id"), nullable=False)
    part_no = Column(Integer)
    user_id = Column(ForeignKey("User.telegram_id"), nullable=False)
    part_start = Column(DateTime(timezone=False))
    part_end = Column(DateTime(timezone=False))

    # relations
    User = relationship('User', back_populates='Khatma_Parts_Done_List')
    Khatma_Done = relationship('Khatma_Done', back_populates='Khatma_Parts_List', lazy="immediate")


class Quran_File(Base):
    __tablename__ = 'Quran_File'
    file_id = Column(Integer, primary_key=True, unique=True, index=True)
    telegram_file_id = Column(String, nullable=False)
