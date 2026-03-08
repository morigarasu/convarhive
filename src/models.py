from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Integer,
    Index,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    # Base class for all ORM models.
    pass


class Thread(Base):
    """スレッド情報を保存するテーブル"""

    __tablename__ = "threads"

    # 主キー
    id: Mapped[int] = mapped_column(primary_key=True)
    # スレッドタイトル
    title: Mapped[str] = mapped_column(String, nullable=False)
    # スレッドURL(重複不可)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # スレッド作成日時
    # DONE sqlite3の datetime adapterを自分で作るか, SQLAlchemyが対応するのを待つか
    # -> mapper_columnの型の設定ミス IntegerからDateTimeに変更
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # このスレッドに属する投稿一覧
    # back_popilates で Post.thread と対応させる
    posts: Mapped[List["Post"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
    )


class Post(Base):
    """投稿情報を保存するテーブル"""

    __tablename__ = "posts"

    # 主キー
    id: Mapped[int] = mapped_column(primary_key=True)
    # 所属スレッドID(threads.idへの外部キー)
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("threads.id"),
        nullable=False,
    )
    # スレッド内の投稿番号
    post_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # ハンドルネーム
    handle_name: Mapped[str] = mapped_column(String, nullable=False)

    # 投稿日時
    # DONE sqlite3の datetime adapterを自分で作るか, SQLAlchemyが対応するのを待つか
    # -> mapper_columnの型の設定ミス IntegerからDateTimeに変更
    posted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # いいね数
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 投稿本文
    content: Mapped[str] = mapped_column(String, nullable=False)
    # 投稿画像URL (画像がない場合はNULL)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    # 同じスレッド内では post_number は一意にしたいので制約を追加
    __table_args__ = (
        UniqueConstraint("thread_id", "post_number", name="uix_thread_post_number"),
        Index("idx_post_id", "id"),
        Index("idx_post_thread_id", "thread_id"),
    )

    ## リレーション定義
    # この投稿が属するスレッド
    thread: Mapped["Thread"] = relationship(
        back_populates="posts",
    )
    # この投稿が「参照している」投稿一覧
    references: Mapped[List["PostReference"]] = relationship(
        foreign_keys="PostReference.from_post_id",
        back_populates="from_post",
        cascade="all, delete-orphan",
    )
    # この投稿が「参照されている」投稿一覧
    referenced_by: Mapped[List["PostReference"]] = relationship(
        foreign_keys="PostReference.to_post_id",
        back_populates="to_post",
        cascade="all, delete-orphan",
    )


class PostReference(Base):
    """
    投稿同士の参照関係を表す中間テーブル
    """

    __tablename__ = "post_references"

    # 主キー
    id: Mapped[int] = mapped_column(primary_key=True)
    # 参照元投稿 (posts.id)
    from_post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )
    # 参照先投稿 (posts.id)
    to_post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )

    # Index作成
    __table_args__ = (
        Index("idx_post_ref_from", "from_post_id"),
        Index("idx_post_ref_to", "to_post_id"),
    )

    ## リレーション定義
    # 参照元のPost
    from_post: Mapped["Post"] = relationship(
        foreign_keys=[from_post_id], back_populates="references"
    )
    # 参照先のPost
    to_post: Mapped["Post"] = relationship(
        foreign_keys=[to_post_id], back_populates="referenced_by"
    )
