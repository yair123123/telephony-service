"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "call_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_call_id", sa.String(length=128), nullable=False),
        sa.Column("from_phone", sa.String(length=32), nullable=False),
        sa.Column("to_phone", sa.String(length=32), nullable=False),
        sa.Column("direction", sa.Enum("INBOUND", "OUTBOUND", name="calldirection"), nullable=False),
        sa.Column(
            "current_state",
            sa.Enum(
                "INCOMING",
                "ASK_ORIGIN",
                "RECORD_ORIGIN",
                "ASK_DESTINATION",
                "RECORD_DESTINATION",
                "ASK_NOTES",
                "RECORD_NOTES",
                "PROCESSING_ORDER",
                "PLAY_SUMMARY",
                "AWAIT_CONFIRMATION",
                "SEARCHING_DRIVER_MESSAGE",
                "CONNECT_DRIVER",
                "CONNECT_CUSTOMER",
                "FINISHED",
                "FAILED",
                name="callstate",
            ),
            nullable=False,
        ),
        sa.Column("status", sa.Enum("ACTIVE", "FINISHED", "FAILED", name="callsessionstatus"), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("ride_id", sa.Integer(), nullable=True),
        sa.Column(
            "last_routing_action",
            sa.Enum(
                "NEW_ORDER",
                "PLAY_SEARCHING_MESSAGE",
                "CONNECT_TO_DRIVER",
                "CONNECT_TO_CUSTOMER",
                "PLAY_NO_ACTIVE_RIDE",
                "PLAY_GENERIC_MESSAGE",
                name="routingaction",
            ),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_call_sessions_provider_call_id", "call_sessions", ["provider_call_id"], unique=True)

    op.create_table(
        "call_recordings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("call_session_id", sa.Integer(), sa.ForeignKey("call_sessions.id"), nullable=False),
        sa.Column("kind", sa.Enum("ORIGIN", "DESTINATION", "NOTES", name="recordingkind"), nullable=False),
        sa.Column("provider_recording_id", sa.String(length=128), nullable=True),
        sa.Column("recording_url", sa.String(length=1024), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_call_recordings_call_session_id", "call_recordings", ["call_session_id"], unique=False)

    op.create_table(
        "call_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("call_session_id", sa.Integer(), sa.ForeignKey("call_sessions.id"), nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )
    op.create_index("ix_call_events_call_session_id", "call_events", ["call_session_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_call_events_call_session_id", table_name="call_events")
    op.drop_table("call_events")
    op.drop_index("ix_call_recordings_call_session_id", table_name="call_recordings")
    op.drop_table("call_recordings")
    op.drop_index("ix_call_sessions_provider_call_id", table_name="call_sessions")
    op.drop_table("call_sessions")

    sa.Enum(name="recordingkind").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="routingaction").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="callsessionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="callstate").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="calldirection").drop(op.get_bind(), checkfirst=True)
