from sqlalchemy import Column, DateTime, Integer, String, Text, func
from app.db.database import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), nullable=False)
    sector = Column(String(255), nullable=False)
    image_name = Column(String(255), nullable=False)
    image_path = Column(Text, nullable=False)
    people_count = Column(Integer, nullable=False, default=0)
    rules_count = Column(Integer, nullable=False, default=0)
    status_summary = Column(Text, nullable=False, default="{}")
    result_path = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
