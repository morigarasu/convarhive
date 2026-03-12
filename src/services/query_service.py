from enum import Enum
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.repository import (
    ThreadRepository,
    PostRepository,
    PostReferenceRepository,
    SearchRepository,
)
from models import Thread, Post, PostReference


class ThreadOrder(str, Enum):
    LATEST = "latest"
    OLDEST = "oldest"
    MOST_POSTS = "most_posts"
    ACTIVE = "active"


class PostOrder(str, Enum):
    LATEST = "latest"
    OLDEST = "oldest"
    LIKES = "likes"
    REFED = "refed"


class Query:
    """
    検索や, ThreadやPostの取得
    """

    def __init__(self, session: Session):
        self.session = session

    # 検索機能
    def search_post(self, keyword: str) -> list[Post]:
        """
        Post全文検索
        database.SearchRepository.search_post() へのリンク
        """
        return SearchRepository(self.session).search_post(keyword)

    def search_thread(self, keyword: str) -> list[Thread]:
        """
        Threadタイトル検索
        database.SearchRepository.search_thread() へのリンク
        """
        return SearchRepository(self.session).search_thread(keyword)

    '''
    def dsl_search_post(DSL: str) -> Post | Thread | None
        """
        DSLでPostを検索する
        """
    '''

    # Thread取得
    def get_thread_by_id(self, thread_id: int) -> Thread | None:
        """
        取得するThreadをidで指定
        一致するThreadがないときは, Noneを返す
        """
        return ThreadRepository(self.session).get_by_id(thread_id)

    def get_thread_by_url(self, thread_url: str) -> Thread | None:
        """
        取得するThreadをurlで指定
        一致するThreadがないときは, Noneを返す
        """
        return ThreadRepository(self.session).get_by_url(thread_url)

    def get_list_threads(
        self,
        limit: int = 10,
        page: int = 1,
        orderby: ThreadOrder = ThreadOrder.LATEST,
    ) -> list[Thread]:
        """
        Threadのリストを取得.
        limit: 返されるThreadの最大量.
        page: limit*(page-1)+1番目からlimit*page番目までThreadを取得する. pageは1以上である必要があります
        orderby: Threadの並び替えの基準 LATEST, OLDEST, MOST_POSTS, ACTIVE を指定することができます.
        """
        query = self.session.query(Thread)
        offset = (page - 1) * limit

        if orderby == ThreadOrder.LATEST:
            return (
                query.order_by(Thread.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
        elif orderby == ThreadOrder.OLDEST:
            return query.order_by(Thread.created_at).offset(offset).limit(limit).all()
        elif orderby == ThreadOrder.MOST_POSTS:
            return (
                self.session.query(Thread, func.count(Post.id).label("post_count"))
                .outerjoin(Post)
                .group_by(Thread.id)
                .order_by(func.count(Post.id).desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
        elif orderby == ThreadOrder.ACTIVE:
            pass

    def get_thread_stats(thread_id):
        """
        Threadの
        投稿数
        平均いいね
        最初の投稿
        最後の投稿
        を取得
        """
        pass

    # Post取得
    def get_posts_by_thread_id(self, thread_id: int) -> list[Post]:
        return self.get_thread_by_id(thread_id).posts

    def get_replies(self, post_id: int) -> list[Post]:
        """
        指定したPostに対する返信のlistを返す.
        """
        return PostReferenceRepository(self.session).get_references_to(post_id)

    def get_referenced_posts(self, post_id: int) -> list[Post]:
        """
        指定したPostが参照するPostのlistを返す.
        """
        return PostReferenceRepository(self.session).get_references_from(post_id)

    def get_post_by_thread_and_postnum(self, thread_id: int, post_number: int) -> Post:
        """
        Thread.idとPost. post_numberからPostを取得する
        """
        return PostRepository(self.session).get_by_thread_and_postnum(
            thread_id, post_number
        )

    def get_list_posts(
        self,
        thread_id: int,
        limit: int = 10,
        page: int = 1,
        orderby: PostOrder = PostOrder.LATEST,
    ) -> list[Post]:
        """
        Postのリストを取得.
        thread_id: どのスレッドでのPostを対象にするか. thread_id = 0 としたとき, すべてのPostが対象となる
        limit: 返されるPostの最大量.
        page: limit*(page-1)+1番目からlimit*page番目までPostを取得する. pageは1以上である必要があります
        orderby: Postの並び替えの基準 LATEST, OLDEST, LIKES, REFED を指定することができる.
        """
        query = self.session.query(Post)
        offset = (page - 1) * limit

        if orderby == PostOrder.LATEST:
            return (
                query.order_by(Post.posted_at.desc()).offset(offset).limit(limit).all()
            )
        elif orderby == PostOrder.OLDEST:
            return query.order_by(Post.posted_at).offset(offset).limit(limit).all()
        elif orderby == PostOrder.LIKES:
            return query.order_by(Post.likes).offset(offset).limit(limit).all()
        elif orderby == PostOrder.REFED:
            """
            もし queryの代わりに
            ```python
            self.session.query(
                Post,
                func.count(PostReference.to_post_id).label("post_ref_count"),
                )
            ```
           を使った場合, 返り値は (<models.Post>, number)の形になる
            """

            return (
                query.outerjoin(PostReference, Post.id == PostReference.to_post_id)
                .group_by(Post.id)
                .order_by(func.count(PostReference.to_post_id).desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
