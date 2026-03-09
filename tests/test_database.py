from database.repository import (
    ThreadRepository,
    PostRepository,
    PostReferenceRepository,
    SearchRepository,
)
from setup_test_db import setup_test_db


def test_thread_repo():
    SessionLocal = setup_test_db()

    with SessionLocal() as session:
        thread_repo = ThreadRepository(session)
        thread_by_id = thread_repo.get_by_id(1)
        thread_by_url = thread_repo.get_by_url("http://example.com/board/123456")

        assert thread_by_id.title == "テストスレ"
        assert thread_by_url.title == "テストスレ"


def test_post_repo():
    SessionLocal = setup_test_db()

    with SessionLocal() as session:
        post_repo = PostRepository(session)

        post_by_id = post_repo.get_by_id(1)
        post_thread_and_num = post_repo.get_by_thread_and_postnum(1, 2)
        posts = post_repo.list_by_thread(1)

        assert post_by_id.content == "これはテスト投稿です"
        assert post_thread_and_num.content == ">>1 それな"

        assert len(posts) == 3
        assert posts[2].content == ">>1 kwsk"


def test_post_ref_repo():
    SessionLocal = setup_test_db()

    with SessionLocal() as session:
        ref_repo = PostReferenceRepository(session)
        refposts_from1 = ref_repo.get_references_from(1)
        refposts_from2 = ref_repo.get_references_from(2)

        refposts_to1 = ref_repo.get_references_to(1)

        assert len(refposts_from1) == 0

        assert len(refposts_from2) == 1
        assert refposts_from2[0].content == "これはテスト投稿です"

        assert len(refposts_to1) == 2
        assert refposts_to1[0].content == ">>1 それな"
        assert refposts_to1[1].content == ">>1 kwsk"


def test_search_repo():
    SessionLocal = setup_test_db()

    with SessionLocal() as session:
        search_repo = SearchRepository(session)

        posts = search_repo.search_post("テスト")
        threads = search_repo.search_thread("テスト")

        assert posts[0].post_number == 1
        assert threads[0].url == "http://example.com/board/123456"
