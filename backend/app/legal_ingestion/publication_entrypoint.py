"""Server-side configuration for the V2 PostgreSQL publication adapter."""
from __future__ import annotations

import os

from .publication import PublicationAdapter, postgres_connection_factory


def configured_publication_adapter(*, batch_size: int = 100) -> PublicationAdapter:
    """Read the pilot DSN without opening a connection or exposing its value."""
    dsn = os.environ.get("MYKE_LEGAL_DATABASE_URL")
    if not dsn:
        raise RuntimeError("MYKE_LEGAL_DATABASE_URL is required for V2 publication")
    return PublicationAdapter(postgres_connection_factory(dsn), batch_size=batch_size)
