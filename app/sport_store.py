"""Sport Store - JSON-based data storage"""
from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path


class SportStore:
    """JSON file-based storage for sport complex data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._collections = ["clients", "trainers", "services", "bookings", "memberships"]
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure all collection files exist"""
        for collection in self._collections:
            filepath = self.data_dir / f"{collection}.json"
            if not filepath.exists():
                filepath.write_text("[]")
    
    def _get_filepath(self, collection: str) -> Path:
        """Get the filepath for a collection"""
        return self.data_dir / f"{collection}.json"
    
    def _read_collection(self, collection: str) -> List[Dict]:
        """Read a collection from file"""
        filepath = self._get_filepath(collection)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _write_collection(self, collection: str, data: List[Dict]):
        """Write a collection to file"""
        filepath = self._get_filepath(collection)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add(self, collection: str, item: Dict, id_field: str = "id") -> Dict:
        """Add an item to a collection"""
        data = self._read_collection(collection)
        
        # Auto-generate ID if not present
        if id_field not in item:
            max_id = max((d.get(id_field, 0) for d in data), default=0)
            item[id_field] = max_id + 1
        
        data.append(item)
        self._write_collection(collection, data)
        return item
    
    def list_all(self, collection: str) -> List[Dict]:
        """List all items in a collection"""
        return self._read_collection(collection)
    
    def get(self, collection: str, id_field: str, id_value: Any) -> Optional[Dict]:
        """Get a single item by ID"""
        data = self._read_collection(collection)
        for item in data:
            if item.get(id_field) == id_value:
                return item
        return None
    
    def update(self, collection: str, id_field: str, id_value: Any, updates: Dict) -> Dict:
        """Update an item in a collection"""
        data = self._read_collection(collection)
        for i, item in enumerate(data):
            if item.get(id_field) == id_value:
                data[i].update(updates)
                self._write_collection(collection, data)
                return data[i]
        raise ValueError(f"Item with {id_field}={id_value} not found")
    
    def delete(self, collection: str, id_field: str, id_value: Any) -> bool:
        """Delete an item from a collection"""
        data = self._read_collection(collection)
        original_len = len(data)
        data = [item for item in data if item.get(id_field) != id_value]
        
        if len(data) < original_len:
            self._write_collection(collection, data)
            return True
        return False
    
    def filter(self, collection: str, **filters) -> List[Dict]:
        """Filter items in a collection"""
        data = self._read_collection(collection)
        result = []
        
        for item in data:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                result.append(item)
        
        return result
