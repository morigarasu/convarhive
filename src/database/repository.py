"""
DB操作をまとめる層
- CRUD操作
- FTS5検索
- commitは行わない (呼び出し元が管理)
"""

from sqlalchemy import text
from sqlalchemy.orm import Session

from models import (
    Thread,
    Post,
    PostReference,
)


class ThreadRepository:
    """Threadの情報を管理"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, thread: Thread):
        self.session.add(thread)

    def get_by_id(self, thread_id: int) -> Thread | None:
        return self.session.get(Thread, thread_id)

    def get_by_url(self, url: str) -> Thread | None:
        return self.session.query(Thread).filter_by(url=url).first()


class PostRepository:
    """Postの情報を管理"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, post: Post):
        """
        Postを**1つ**追加する
        """
        self.session.add(post)

    def add_all(self, posts: list[Post]):
        """
        PostのListを使って、まとめてPostを追加する
        """
        self.session.add_all(posts)

    def get_by_id(self, post_id: int) -> Post | None:
        return self.session.get(Post, post_id)

    def get_by_thread_and_postnum(self, thread_id: int, post_num: int) -> Post | None:
        """
        指定したthreadのidと投稿の番号に合致するPostを返す
        """
        return (
            self.session.query(Post)
            .filter_by(thread_id=thread_id, post_num=post_num)
            .first()
        )

    def list_by_thread(self, thread_id: int):
        """
        idで指定したスレッドに属するPostをlistで返す
        """
        return (
            self.session.query(Post)
            .filter_by(thread_id=thread_id)
            .order_by(Post.post_num)
            .all()
        )


class PostReferenceRepository:
    """Post 同士の参照を管理"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, reference: PostReference):
        """
        PostReferenceを**1つ**追加する
        """
        self.session.add(reference)

    def add_all(self, references: list[PostReference]):
        """
        PostReferenceのListを使って、まとめてPostReferenceを追加する
        """
        self.session.add_all(references)

    def get_references_from(self, post_id: int) -> list[Post]:
        """
        指定した投稿によって参照されている投稿のリストを返す
        """
        refs_from = (
            self.session.query(PostReference).filter_by(from_post_id=post_id).all()
        )
        return [r.to_post for r in refs_from]

    def get_references_to(self, post_id: int) -> list[Post]:
        """
        指定した投稿が参照している投稿のリストを返す
        """
        refs_to = self.session.query(PostReference).filter_by(to_post_id=post_id).all()
        return [r.from_post for r in refs_to]


# FTS5関連処理
class SearchRepository:
    def __init__(self, session: Session):
        self.session = session

    # FTS5 仮想テーブル作成
    def init_fts_tables(self):
        # TODO 初期化が複数回行われたときの処理
        # 再インデックスが必要になったことを考えれば不要か？
        """
        FTS5の仮想テーブルを作成する
        初期化時に1回だけ呼ぶ想定
        """

        posts_fts_sql = """
            CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts
            USING fts5(
                post_id UNINDEXED,
                content,
                tokenize = 'trigram',
            );
        """

        threads_fts_sql = """
            CREATE VIRTUAL TABLE IF NOT EXISTS threads_fts
            USING fts5(
                thread_id UNINDEXED,
                title,
                tokenize = 'trigram',
            );
        """

        for sql in [posts_fts_sql, threads_fts_sql]:
            self.session.execute(text(sql))

    # 投稿をFTSインデックスへ追加
    def add2post_index(self, post_id: int, content: str):
        """
        投稿をFTSインデックスに追加する
        """
        self.session.execute(
            text("""
                INSERT INTO posts_fts (post_id, content)
                VALUES (:post_id, :content)
            """),
            {"post_id": post_id, "content": content},
        )

    # スレッドをFTSインデックスへ追加
    def add2thread_index(self, thread_id: int, title: str):
        """
        投稿をFTSインデックスに追加する
        """
        self.session.execute(
            text("""
                INSERT INTO threads_fts (thread_id, title)
                VALUES (:thread_id, :title)
            """),
            {"thread_id": thread_id, "title": title},
        )

    def rebuild(self):
        """
        現在存在するFTS5のテーブルを削除し、
        すべての投稿をFTSインデックスに追加し直す
        """
        self.session.execute(text("DELETE FROM posts_fts"))
        posts = self.session.query(Post).all()
        for post in posts:
            self.add2post_index(post.id, post.content)

        self.session.execute(text("DELETE FROM threads_fts"))
        threads = self.session.query(Thread).all()
        for thread in threads:
            self.add2thread_index(thread.id, thread.title)

    def search_post(self, keyword: str) -> list[Post]:
        """
        MATCH を使った全文検索
        """
        result = self.session.execute(
            text("""
                SELECT post_id
                FROM posts_fts
                WHERE posts_fts MATCH :query
            """),
            {"query": keyword},
        )

        post_ids = [row[0] for row in result.fetchall()]

        if not post_ids:
            return []
        else:
            return self.session.query(Post).filter(Post.id.in_(post_ids)).all()

    def search_thread(self, keyword: str) -> list[Thread]:
        """
        MATCH を使った全文検索
        """
        result = self.session.execute(
            text("""
                SELECT thread_id
                FROM threads_fts
                WHERE threads_fts MATCH :query
            """),
            {"query": keyword},
        )

        thread_ids = [row[0] for row in result.fetchall()]

        if not thread_ids:
            return []
        else:
            return self.session.query(Thread).filter(Thread.id.in_(thread_ids)).all()
