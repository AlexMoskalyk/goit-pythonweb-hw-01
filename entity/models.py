from datetime import datetime

from sqlalchemy import ForeignKey, func, DateTime, String, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    students: Mapped[list["Student"]] = relationship(back_populates='group')


class Teacher(Base):
    __tablename__ = 'teachers'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    second_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    subjects: Mapped[list["Subject"]] = relationship(back_populates='teacher')

class Subject(Base):
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id', ondelete="SET NULL"), nullable=False)

    teacher: Mapped["Teacher"] = relationship(back_populates='subjects')
    grades: Mapped[list["Grade"]] = relationship(back_populates='subject', cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.id', ondelete="SET NULL"), nullable=False)

    group: Mapped["Group"] = relationship(back_populates='students')
    grades: Mapped[list["Grade"]] = relationship(back_populates='student', cascade="all, delete-orphan")

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, ' ', cls.last_name)

    def __repr__(self):
        return f"Student(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, phone={self.phone})"


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id', ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id', ondelete="CASCADE"), nullable=False)
    grade: Mapped[float] = mapped_column(Float, nullable=False)
    date_received: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    student: Mapped["Student"] = relationship(back_populates='grades')
    subject: Mapped["Subject"] = relationship(back_populates='grades')

