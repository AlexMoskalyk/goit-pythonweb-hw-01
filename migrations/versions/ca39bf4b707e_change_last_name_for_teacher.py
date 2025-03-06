"""Change last_name for Teacher

Revision ID: ca39bf4b707e
Revises: cf3a1c438c74
Create Date: 2025-03-05 21:30:24.269638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca39bf4b707e'
down_revision: Union[str, None] = 'cf3a1c438c74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Додаємо новий стовпець без обмеження NOT NULL
    op.add_column('teachers', sa.Column('second_name', sa.String(length=100), nullable=True))

    # 2. Копіюємо дані зі старого стовпця в новий
    op.execute("UPDATE teachers SET second_name = last_name")

    # 3. Встановлюємо обмеження NOT NULL для нового стовпця
    op.alter_column('teachers', 'second_name', nullable=False)

    # 4. Видаляємо старий стовпець
    op.drop_column('teachers', 'last_name')


def downgrade() -> None:
    """Downgrade schema."""
    # Аналогічно для відкату змін
    op.add_column('teachers', sa.Column('last_name', sa.VARCHAR(length=100), nullable=True))
    op.execute("UPDATE teachers SET last_name = second_name")
    op.alter_column('teachers', 'last_name', nullable=False)
    op.drop_column('teachers', 'second_name')
