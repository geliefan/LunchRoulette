#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CacheService - キャッシュサービスクラス
SQLiteを使用したキャッシング機能を提供

このクラスは以下の機能を提供します:
- キャッシュデータの保存・取得
- TTL（Time To Live）ベースの有効期限チェック
- キャッシュキーの生成とデータシリアライゼーション
- 自動的な期限切れデータクリーンアップ
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union
from database import get_db_connection, cleanup_expired_cache


class CacheService:
    """
    SQLiteを使用したキャッシングサービス
    
    外部API呼び出しの結果をキャッシュし、レート制限対策と
    パフォーマンス向上を実現する。
    """
    
    def __init__(self, db_path: str = 'cache.db', default_ttl: int = 600):
        """
        CacheServiceを初期化
        
        Args:
            db_path (str): SQLiteデータベースファイルのパス
            default_ttl (int): デフォルトTTL（秒）、デフォルトは10分
        """
        self.db_path = db_path
        self.default_ttl = default_ttl
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        キャッシュキーを生成
        
        プレフィックスとキーワード引数からユニークなキャッシュキーを生成する。
        同じパラメータに対しては常に同じキーが生成される。
        
        Args:
            prefix (str): キャッシュキーのプレフィックス（例: "weather", "restaurant"）
            **kwargs: キャッシュキー生成に使用するパラメータ
            
        Returns:
            str: 生成されたキャッシュキー
            
        Example:
            >>> cache = CacheService()
            >>> key = cache.generate_cache_key("weather", lat=35.6762, lon=139.6503)
            >>> print(key)  # "weather_a1b2c3d4e5f6..."
        """
        # パラメータを文字列に変換してソート（一貫性のため）
        params_str = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)
        
        # SHA256ハッシュを生成
        hash_object = hashlib.sha256(params_str.encode('utf-8'))
        hash_hex = hash_object.hexdigest()[:16]  # 16文字に短縮
        
        return f"{prefix}_{hash_hex}"
    
    def serialize_data(self, data: Any) -> str:
        """
        データをJSON文字列にシリアライズ
        
        Args:
            data (Any): シリアライズするデータ
            
        Returns:
            str: JSON文字列
            
        Raises:
            ValueError: シリアライズできないデータの場合
        """
        try:
            return json.dumps(data, ensure_ascii=False, default=str)
        except (TypeError, ValueError) as e:
            raise ValueError(f"データのシリアライズに失敗: {e}")
    
    def deserialize_data(self, data_str: str) -> Any:
        """
        JSON文字列をデータにデシリアライズ
        
        Args:
            data_str (str): JSON文字列
            
        Returns:
            Any: デシリアライズされたデータ
            
        Raises:
            ValueError: デシリアライズできない文字列の場合
        """
        try:
            return json.loads(data_str)
        except (TypeError, ValueError) as e:
            raise ValueError(f"データのデシリアライズに失敗: {e}")
    
    def is_cache_valid(self, expires_at: datetime) -> bool:
        """
        キャッシュの有効性をチェック
        
        Args:
            expires_at (datetime): キャッシュの有効期限
            
        Returns:
            bool: 有効な場合True、期限切れの場合False
        """
        return datetime.now() < expires_at
    
    def set_cached_data(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        キャッシュデータを保存
        
        Args:
            key (str): キャッシュキー
            data (Any): 保存するデータ
            ttl (int, optional): TTL（秒）。Noneの場合はdefault_ttlを使用
            
        Returns:
            bool: 保存が成功した場合True
            
        Example:
            >>> cache = CacheService()
            >>> success = cache.set_cached_data("weather_tokyo", {"temp": 25}, 600)
            >>> print(success)  # True
        """
        try:
            # TTLが指定されていない場合はデフォルト値を使用
            if ttl is None:
                ttl = self.default_ttl
            
            # 有効期限を計算
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # データをシリアライズ
            serialized_data = self.serialize_data(data)
            
            # データベースに保存
            with get_db_connection(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache 
                    (cache_key, data, expires_at) 
                    VALUES (?, ?, ?)
                ''', (key, serialized_data, expires_at))
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"キャッシュ保存エラー (key: {key}): {e}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        キャッシュデータを取得
        
        Args:
            key (str): キャッシュキー
            
        Returns:
            Any: キャッシュされたデータ。存在しないか期限切れの場合はNone
            
        Example:
            >>> cache = CacheService()
            >>> data = cache.get_cached_data("weather_tokyo")
            >>> if data:
            ...     print(f"Temperature: {data['temp']}")
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT data, expires_at FROM cache 
                    WHERE cache_key = ?
                ''', (key,))
                
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                # 有効期限をチェック
                expires_at = datetime.fromisoformat(row['expires_at'])
                if not self.is_cache_valid(expires_at):
                    # 期限切れの場合は削除
                    self._delete_cache_entry(key)
                    return None
                
                # データをデシリアライズして返す
                return self.deserialize_data(row['data'])
                
        except Exception as e:
            print(f"キャッシュ取得エラー (key: {key}): {e}")
            return None
    
    def _delete_cache_entry(self, key: str) -> bool:
        """
        指定されたキャッシュエントリを削除（内部メソッド）
        
        Args:
            key (str): 削除するキャッシュキー
            
        Returns:
            bool: 削除が成功した場合True
        """
        try:
            with get_db_connection(self.db_path) as conn:
                conn.execute('DELETE FROM cache WHERE cache_key = ?', (key,))
                conn.commit()
            return True
        except Exception as e:
            print(f"キャッシュ削除エラー (key: {key}): {e}")
            return False
    
    def delete_cached_data(self, key: str) -> bool:
        """
        キャッシュデータを削除
        
        Args:
            key (str): 削除するキャッシュキー
            
        Returns:
            bool: 削除が成功した場合True
        """
        return self._delete_cache_entry(key)
    
    def clear_expired_cache(self) -> int:
        """
        期限切れのキャッシュデータをすべて削除
        
        Returns:
            int: 削除されたレコード数
        """
        return cleanup_expired_cache(self.db_path)
    
    def clear_all_cache(self) -> bool:
        """
        すべてのキャッシュデータを削除
        
        Returns:
            bool: 削除が成功した場合True
        """
        try:
            with get_db_connection(self.db_path) as conn:
                conn.execute('DELETE FROM cache')
                conn.commit()
            return True
        except Exception as e:
            print(f"全キャッシュ削除エラー: {e}")
            return False
    
    def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        キャッシュの詳細情報を取得
        
        Args:
            key (str): キャッシュキー
            
        Returns:
            dict: キャッシュ情報（作成日時、有効期限、データサイズなど）
        """
        try:
            with get_db_connection(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT created_at, expires_at, LENGTH(data) as data_size
                    FROM cache WHERE cache_key = ?
                ''', (key,))
                
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                expires_at = datetime.fromisoformat(row['expires_at'])
                created_at = datetime.fromisoformat(row['created_at'])
                
                return {
                    'key': key,
                    'created_at': created_at,
                    'expires_at': expires_at,
                    'is_valid': self.is_cache_valid(expires_at),
                    'data_size': row['data_size'],
                    'ttl_remaining': max(0, (expires_at - datetime.now()).total_seconds())
                }
                
        except Exception as e:
            print(f"キャッシュ情報取得エラー (key: {key}): {e}")
            return None


# 使用例とテスト用コード
if __name__ == '__main__':
    """
    CacheServiceのテスト実行
    """
    print("CacheService テスト実行")
    print("=" * 40)
    
    # CacheServiceインスタンス作成
    cache = CacheService()
    
    # テストデータ
    test_data = {
        'temperature': 25.5,
        'condition': 'sunny',
        'location': '東京',
        'timestamp': datetime.now().isoformat()
    }
    
    # キャッシュキー生成テスト
    cache_key = cache.generate_cache_key('weather', lat=35.6762, lon=139.6503)
    print(f"✓ キャッシュキー生成: {cache_key}")
    
    # データ保存テスト
    if cache.set_cached_data(cache_key, test_data, ttl=60):
        print("✓ キャッシュデータ保存成功")
    else:
        print("✗ キャッシュデータ保存失敗")
    
    # データ取得テスト
    cached_data = cache.get_cached_data(cache_key)
    if cached_data:
        print(f"✓ キャッシュデータ取得成功: {cached_data['condition']}")
    else:
        print("✗ キャッシュデータ取得失敗")
    
    # キャッシュ情報取得テスト
    cache_info = cache.get_cache_info(cache_key)
    if cache_info:
        print(f"✓ キャッシュ情報: TTL残り {cache_info['ttl_remaining']:.1f}秒")
    
    # 期限切れキャッシュクリーンアップテスト
    expired_count = cache.clear_expired_cache()
    print(f"✓ 期限切れキャッシュクリーンアップ: {expired_count}件削除")
    
    print("テスト完了")