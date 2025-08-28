from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    meli_user_id = Column(String(64), index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    token_type = Column(String(20))
    scope = Column(Text)
    expires_at = Column(DateTime(timezone=True))  # UTC
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
