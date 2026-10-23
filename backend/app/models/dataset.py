import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, JSON
from app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    adapter_type = Column(String(50), nullable=False)  # UNSW-NB15, NF-UNSW-NB15-v2, NF-BoT-IoT-v2, ToN-IoT, Edge-IIoTset, CIC-IDS2017, generic
    file_path = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    total_columns = Column(Integer, default=0)
    benign_count = Column(Integer, default=0)
    malicious_count = Column(Integer, default=0)
    
    # Preprocessing & schema metadata
    column_info = Column(JSON, default=dict)  # list of {name, type, missing_count, sample_values}
    class_distribution = Column(JSON, default=dict)  # {class_name: count}
    is_validated = Column(Boolean, default=False)
    is_sample = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
