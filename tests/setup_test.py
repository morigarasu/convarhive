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
from scraper.base.schemas import PostData


def create_db(echo: bool = False):
    engine, SessionLocal = create_engine_and_session("sqlite:///:memory:", echo=echo)
    init_db(engine)
    return SessionLocal


def setup_test_db(echo: bool = False):

    SessionLocal = create_db(echo)

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


class mok_scraper:
    def __init__(self, dummy_data):
        self.dd = dummy_data

    def scrape_thread_and_posts(self, url: str):
        return (self.dd["thread"], self.dd["post_datas"])


test_date = datetime(2026, 3, 2, 13, 35, 0)
dummy_data = {
    "thread": Thread(
        title="テストスレ", url="https://example.com/board/100000", created_at=test_date
    ),
    "post_datas": [
        PostData(
            post_number=1,
            handle_name="anon1",
            posted_at=test_date,
            likes=0,
            content="テストスレッド作成",
            image_urls=[
                "https://example.com/img/1",
                "https://example.com/img/2",
            ],
            ref_to_nums=[],
        ),
        PostData(
            post_number=2,
            handle_name="anon",
            posted_at=test_date,
            likes=3,
            content=">>1\n立て乙",
            image_urls=[],
            ref_to_nums=[1],
        ),
        PostData(
            post_number=3,
            handle_name="anon",
            posted_at=test_date,
            likes=0,
            content=">>1 >>2\nお前ら仲いいな",
            image_urls=[],
            ref_to_nums=[1, 2],
        ),
        PostData(
            post_number=4,
            handle_name="anon",
            posted_at=test_date,
            likes=0,
            content="こんにちは",
            image_urls=[
                "https://example.com/img/3",
            ],
            ref_to_nums=[],
        ),
        PostData(
            post_number=5,
            handle_name="anon",
            posted_at=test_date,
            likes=0,
            content="Hello",
            image_urls=[],
            ref_to_nums=[1, 2, 3],
        ),
    ],
}
