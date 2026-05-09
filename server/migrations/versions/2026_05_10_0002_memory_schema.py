"""memory_schema — memory_items table for the M1.2 memory layer

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-10
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels = None
depends_on = None


def _uuid_type() -> sa.types.TypeEngine[object]:
    bind = op.get_bind() if op.get_context().bind is not None else None
    dialect = bind.dialect.name if bind is not None else "postgresql"
    return postgresql.UUID(as_uuid=True) if dialect == "postgresql" else sa.String(36)


def upgrade() -> None:
    uuid_t = _uuid_type()
    op.create_table(
        "memory_items",
        sa.Column("id", uuid_t, primary_key=True),
        sa.Column(
            "user_id",
            uuid_t,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(32), nullable=False, server_default="note"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("vector_id", sa.String(64), nullable=True, unique=True),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("source", sa.String(128), nullable=True),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_memory_items_user_id", "memory_items", ["user_id"])
    op.create_index("ix_memory_user_kind", "memory_items", ["user_id", "kind"])
    op.create_index(
        "ix_memory_user_created", "memory_items", ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_memory_user_created", table_name="memory_items")
    op.drop_index("ix_memory_user_kind", table_name="memory_items")
    op.drop_index("ix_memory_items_user_id", table_name="memory_items")
    op.drop_table("memory_items")
