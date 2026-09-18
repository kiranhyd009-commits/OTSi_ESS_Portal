"""Database utilities for Supabase connection"""
import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any, cast
import logging

logger = logging.getLogger(__name__)


class SupabaseDB:
    """Supabase database wrapper"""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client"""
        if cls._instance is None:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            
            cls._instance = create_client(supabase_url, supabase_key)
        
        assert cls._instance is not None
        return cls._instance

    @classmethod
    def get_table(cls, table: str):
        """Get table reference with optional custom schema (e.g. ess_portal or public)"""
        client = cls.get_client()
        schema = os.getenv('SUPABASE_SCHEMA', 'public').strip()
        if schema and schema != 'public':
            return client.schema(schema).table(table)
        return client.table(table)
    
    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert a record"""
        try:
            response = SupabaseDB.get_table(table).insert(data).execute()
            return cast(Dict[str, Any], response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Insert error in {table}: {str(e)}")
            raise
    
    @staticmethod
    def insert_many(table: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insert multiple records"""
        try:
            response = SupabaseDB.get_table(table).insert(data).execute()
            return cast(List[Dict[str, Any]], response.data)
        except Exception as e:
            logger.error(f"Batch insert error in {table}: {str(e)}")
            raise
    
    @staticmethod
    def select(table: str, columns: str = "*", filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Select records with optional filters"""
        try:
            query = SupabaseDB.get_table(table).select(columns)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, tuple):
                        op, val = value
                        method = getattr(query, op, None)
                        if method:
                            query = method(key, val)
                    else:
                        query = query.eq(key, value)
            
            response = query.execute()
            return cast(List[Dict[str, Any]], response.data)
        except Exception as e:
            logger.error(f"Select error from {table}: {str(e)}")
            raise
    
    @staticmethod
    def select_one(table: str, filters: Dict) -> Optional[Dict[str, Any]]:
        """Select a single record"""
        try:
            results = SupabaseDB.select(table, "*", filters)
            return cast(Dict[str, Any], results[0]) if results else None
        except Exception as e:
            logger.error(f"Select one error from {table}: {str(e)}")
            raise
    
    @staticmethod
    def update(table: str, filters: Dict, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update records"""
        try:
            query = SupabaseDB.get_table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return cast(Dict[str, Any], response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Update error in {table}: {str(e)}")
            raise
    
    @staticmethod
    def delete(table: str, filters: Dict) -> bool:
        """Delete records"""
        try:
            query = SupabaseDB.get_table(table).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Delete error from {table}: {str(e)}")
            raise
    
    @staticmethod
    def count(table: str, filters: Optional[Dict] = None) -> int:
        """Count records"""
        try:
            query = SupabaseDB.get_table(table).select("id", count="exact")  # type: ignore[arg-type]
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return int(response.count) if response.count is not None else 0
        except Exception as e:
            logger.error(f"Count error on {table}: {str(e)}")
            raise
