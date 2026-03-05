# from datetime import datetime

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
from models import Thread, Post, PostReference


def create_db():
    engine, SessionLocal = create_engine_and_session("sqlite:///:memory:")
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
            # TODO modelsのdatetime adapter待ち
            # created_at=datetime.now(),
        )
        thread_repo.add(thread)
        session.flush()

        # Post作成
        post1 = Post(
            thread_id=thread.id,
            post_num=1,
            handle_name="太郎",
            # TODO modelsのdatetime adapter待ち
            # posted_at=datetime.now(),
            likes=1,
            content="これはテスト投稿です",
        )

        post2 = Post(
            thread_id=thread.id,
            post_num=2,
            handle_name="次郎",
            # TODO modelsのdatetime adapter待ち
            # posted_at=datetime.now(),
            likes=2,
            content=">>1 それな",
        )

        post3 = Post(
            thread_id=thread.id,
            post_num=3,
            handle_name="三郎",
            # TODO modelsのdatetime adapter待ち
            # posted_at=datetime.now(),
            likes=1,
            content=">>1 kwsk",
        )

        posts = [post1, post2, post3]
        post_repo.add_all(posts)
        session.flush()

        # FTSへ追加
        for post in posts:
            search_repo.add2post_index(post.id, post.content)

        search_repo.add2thread_index(thread.id, thread.title)

        # 参照作成
        id_refs = [[post2.id, post1.id], [post3.id, post1.id]]
        for ids in id_refs:
            ref = PostReference(from_post_id=ids[0], to_post_id=ids[1])
            ref_repo.add(ref)

        session.commit()

    return SessionLocal


def test_reference_and_search4post():

    SessionLocal = setup_test_db()
    # 検索テスト
    with SessionLocal() as session:
        search_repo = SearchRepository(session)
        results = search_repo.search_post("テスト")

        assert len(results) == 1
        assert results[0].content == "これはテスト投稿です"

    # 参照テスト
    with SessionLocal() as session:
        ref_repo = PostReferenceRepository(session)

        refs_to_post1 = ref_repo.get_references_to(1)
        refs_from_post2 = ref_repo.get_references_from(2)

        assert len(refs_to_post1) == 2
        assert len(refs_from_post2) == 1

        assert refs_from_post2[0].content == "これはテスト投稿です"


def test_get_and_search4thread():

    SessionLocal = setup_test_db()

    with SessionLocal() as session:
        thread_repo = ThreadRepository(session)

        # thread = thread_repo.get_by_url("http://example.com/board/123456")
        thread = thread_repo.get_by_id(1)

        assert len(thread.posts) == 3
        assert thread.posts[2].content == ">>1 kwsk"

    with SessionLocal() as session:
        search_repo = SearchRepository(session)
        results = search_repo.search_thread("テスト")

        assert len(results) == 1
        assert results[0].title == "テストスレ"

        search_repo.rebuild()
