from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from conf.db import SessionLocal
from entity.models import Student, Grade, Subject, Teacher, Group




# 1️⃣ Знайти 5 студентів із найбільшим середнім балом з усіх предметів.
def select_01(session: Session):
    query = (
        select(Student.full_name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .limit(5)
    )
    return session.execute(query).all()


# 2️⃣ Знайти студента із найвищим середнім балом з певного предмета.
def select_02(session: Session, subject_id: int):
    stmt = (
        select(Student.full_name, func.avg(Grade.grade).label("avg_grade"))
        .join(Grade)
        .where(Grade.subject_id == subject_id)
        .group_by(Student.id)
        .order_by(desc("avg_grade"))
        .limit(1)
    )
    return session.execute(stmt).first()


# 3️⃣ Знайти середній бал у групах з певного предмета.
def select_03(session: Session, subject_id: int):
    stmt = (
        select(Group.name, func.avg(Grade.grade).label("avg_grade"))
        .join(Student)
        .join(Grade)
        .where(Grade.subject_id == subject_id)
        .group_by(Group.id)
        .order_by(desc("avg_grade"))
    )
    return session.execute(stmt).all()


# 4️⃣ Знайти середній бал на потоці (по всій таблиці оцінок).
def select_04(session: Session):
    stmt = select(func.avg(Grade.grade).label("overall_avg_grade"))
    return session.execute(stmt).scalar()


# 5️⃣ Знайти які курси читає певний викладач.
def select_05(session: Session, teacher_id: int):
    stmt = (
        select(Subject.name)
        .where(Subject.teacher_id == teacher_id)
    )
    return session.execute(stmt).all()


# 6️⃣ Знайти список студентів у певній групі.
def select_06(session: Session, group_id: int):
    stmt = (
        select(Student.full_name)
        .where(Student.group_id == group_id)
    )
    return session.execute(stmt).all()


# 7️⃣ Знайти оцінки студентів у окремій групі з певного предмета.
def select_07(session: Session, group_id: int, subject_id: int):
    stmt = (
        select(Student.full_name, Grade.grade, Grade.date_received)
        .join(Grade)
        .where(Grade.subject_id == subject_id, Student.group_id == group_id)
    )
    return session.execute(stmt).all()


# 8️⃣ Знайти середній бал, який ставить певний викладач зі своїх предметів.
def select_08(session: Session, teacher_id: int):
    stmt = (
        select(func.avg(Grade.grade).label("avg_teacher_grade"))
        .join(Subject)
        .where(Subject.teacher_id == teacher_id)
    )
    return session.execute(stmt).scalar()


# 9️⃣ Знайти список курсів, які відвідує певний студент.
def select_09(session: Session, student_id: int):
    stmt = (
        select(Subject.name)
        .join(Grade)
        .where(Grade.student_id == student_id)
        .distinct()
    )
    return session.execute(stmt).all()


# 🔟 Список курсів, які певному студенту читає певний викладач.
def select_10(session: Session, student_id: int, teacher_id: int):
    stmt = (
        select(Subject.name)
        .join(Grade)
        .where(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
        .distinct()
    )
    return session.execute(stmt).all()


if __name__ == "__main__":
    session: Session = SessionLocal()

    print("Знайти 5 студентів із найбільшим середнім балом з усіх предметів:", select_01(session))
    print("Знайти студента із найвищим середнім балом з певного предмета:", select_02(session, 2))
    print("Знайти середній бал у групах з певного предмета:", select_03(session, 2))
    print("Знайти середній бал на потоці:", select_04(session))
    print("Знайти які курси читає певний викладач:", select_05(session, 1))
    print("Знайти список студентів у певній групі:", select_06(session, 3))
    print("Знайти оцінки студентів у окремій групі з певного предмета:", select_07(session, 3, 1))
    print("Знайти середній бал, який ставить певний викладач зі своїх предметів:", select_08(session, 1))
    print("Знайти список курсів, які відвідує певний студент:", select_09(session, 1))
    print("Список курсів, які певному студенту читає певний викладач:", select_10(session, 1, 2))

    session.close()

