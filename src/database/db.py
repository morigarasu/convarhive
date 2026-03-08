"""
データベース接続と初期化を管理するモジュール
責務：
- DB接続と初期化管理

- Engine生成
- SessionLocal提供
- テーブル作成
- SQLite設定 (外部キー有効化)
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from models import Base


def create_engine_and_session(db_url: str, echo: bool = False):
    """
    EngineとSessionLocalを生成する
    """

    # Engine生成
    engine = create_engine(
        db_url,
        echo=echo,
        future=True,
    )

    # SQLite外部キー有効化
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        # SQLiteではデフォルトで外部キー制約が無効なので, 有効化する
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    # SessionLocal
    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return engine, SessionLocal


# 初期化処理
def init_db(engine):
    """
    通常テーブルを作成する.
    FTS仮想テーブルはRepository側で作成する
    """
    Base.metadata.create_all(bind=engine)
