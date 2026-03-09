from database.db import (
    create_engine_and_session,
    init_db,
)
from database.repository import (
    ThreadRepository,
    PostRepository,
    PostReferenceRepository,
    SearchRepository,
)
from datetime import datetime
from models import Thread, Post, PostReference


def create_db():
    engine, SessionLocal = create_engine_and_session("sqlite:///:memory:", echo=True)
    init_db(engine)
    return SessionLocal


def setup_test_db():

    SessionLocal = create_db()

    # データをdbに追加
    with SessionLocal() as session:
        # Repository生成
        thread_repo = ThreadRepository(session)
        post_repo = PostRepository(session)
        ref_repo = PostReferenceRepository(session)
        search_repo = SearchRepository(session)

        # FTSテーブル作成
        search_repo.init_fts_tables()

        # Thread作成
        thread = Thread(
            title="テストスレ",
            url="http://example.com/board/123456",
            # DONE modelsのdatetime adapter待ち
            # -> mapper_columnの型の設定ミス IntegerからDateTimeに変更
            created_at=datetime(2026, 3, 2, 13, 35, 0),
        )
        thread_repo.add(thread)
        session.flush()

        # Post作成
        post1 = Post(
            thread_id=thread.id,
            post_number=1,
            handle_name="太郎",
            # DONE modelsのdatetime adapter待ち
            # -> mapper_columnの型の設定ミス IntegerからDateTimeに変更
            posted_at=datetime(2026, 3, 2, 13, 35, 0),
            likes=1,
            content="これはテスト投稿です",
        )

        post2 = Post(
            thread_id=thread.id,
            post_number=2,
            handle_name="次郎",
            # DONE modelsのdatetime adapter待ち
            # -> mapper_columnの型の設定ミス IntegerからDateTimeに変更
            posted_at=datetime(2026, 3, 2, 13, 35, 0),
            likes=2,
            content=">>1 それな",
        )

        post3 = Post(
            thread_id=thread.id,
            post_number=3,
            handle_name="三郎",
            # DONE modelsのdatetime adapter待ち
            # -> mapper_columnの型の設定ミス IntegerからDateTimeに変更
            posted_at=datetime(2026, 3, 2, 13, 35, 0),
            likes=1,
            content=">>1 kwsk",
        )

        posts = [post1, post2, post3]
        post_repo.add_all(posts)
        session.flush()

        # FTSへ追加
        for post in posts:
            search_repo.add_to_post_index(post.id, post.content)

        search_repo.add_to_thread_index(thread.id, thread.title)

        # 参照作成
        id_refs = [[post2.id, post1.id], [post3.id, post1.id]]
        for ids in id_refs:
            ref = PostReference(from_post_id=ids[0], to_post_id=ids[1])
            ref_repo.add(ref)

        session.commit()

    return SessionLocal
