"""pairing_codes — single-use device pairing codes (M1.6)

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-10
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels = None
depends_on = None


def _uuid_type() -> sa.types.TypeEngine[object]:
    bind = op.get_bind() if op.get_context().bind is not None else None
    dialect = bind.dialect.name if bind is not None else "postgresql"
    return postgresql.UUID(as_uuid=True) if dialect == "postgresql" else sa.String(36)


def upgrade() -> None:
    uuid_t = _uuid_type()
    op.create_table(
        "pairing_codes",
        sa.Column("id", uuid_t, primary_key=True),
        sa.Column(
            "user_id",
            uuid_t,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(8), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_pairing_codes_user_id", "pairing_codes", ["user_id"])
    op.create_index("ix_pairing_user_id", "pairing_codes", ["user_id"])
    op.create_index("ix_pairing_expires_at", "pairing_codes", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_pairing_expires_at", table_name="pairing_codes")
    op.drop_index("ix_pairing_user_id", table_name="pairing_codes")
    op.drop_index("ix_pairing_codes_user_id", table_name="pairing_codes")
    op.drop_table("pairing_codes")
