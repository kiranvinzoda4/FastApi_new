#!/usr/bin/env python3
import pymysql
from app.config import settings

try:
    connection = pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        port=settings.DB_PORT
    )
    print("✅ Database connection successful")
    connection.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"Database: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}")