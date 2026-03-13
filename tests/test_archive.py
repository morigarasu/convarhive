from services import Archive
from setup_test import create_db, mok_scraper, dummy_data
from database.repository import (
    ThreadRepository,
    PostRepository,
    PostReferenceRepository,
)


def test_archive_thread():
    SessionLocal = create_db()

    with SessionLocal() as session:
        archive_srvs = Archive(session, mok_scraper(dummy_data))
        archive_srvs.archive_thread("test_url")

    with SessionLocal() as session:
        thread_repo = ThreadRepository(session)
        post_repo = PostRepository(session)
        ref_repo = PostReferenceRepository(session)

        assert thread_repo.get_by_id(1).title == "テストスレ"

        assert post_repo.get_by_thread_and_postnum(1, 4).content == "こんにちは"

        refposts_to1 = ref_repo.get_references_to(1)
        assert len(refposts_to1) == 3


def test_update_thread():
    pass
