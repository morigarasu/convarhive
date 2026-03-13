from sqlalchemy.orm import Session
from sqlalchemy import select, func

from scraper.base.schemas import PostData
from models import Post, Image, PostReference
from database.repository import ThreadRepository


class Archive:
    def __init__(self, session: Session, scraper):
        self.session = session
        self.scraper = scraper

    def archive_thread(self, url: str):
        """
        与えられたURLのスレッドをアーカイブし, DBにcommitする
        """
        thread, post_datas = self.scraper.scrape_thread_and_posts(url)

        posts = []
        for pd in post_datas:
            post = self._conv_postdata(pd)
            thread.posts.append(post)
            posts.append(post)

        self.session.add(thread)
        self.session.flush()

        references = self._resolve_references(posts, post_datas)

        self.session.add_all(references)
        self.session.commit()

    def update_thread(self, url: str):
        thread = ThreadRepository(self.session).get_by_url(url)

        if not thread:
            self.archive_thread(url)
            return

        last_post_num = self._get_last_post_num(thread.id)

        # スクレイピング
        thread, post_datas = self.scraper.scrape_thread_and_posts(url)

        # 差分抽出
        new_post_datas = self._filter_new_posts(post_datas, last_post_num)

        # 更新がないときは, 終了する
        if not new_post_datas:
            return

        new_posts = [self._conv_postdata(pd) for pd in new_post_datas]

        # DBを保存
        self.session.add_all(new_posts)
        self.session.flush()

        # Reference生成
        references = self._resolve_references(new_posts, new_post_datas)

        self.session.add_all(references)
        self.session.commit()

    def _get_new_posts(self):
        pass

    def _conv_postdata(self, pd: PostData):
        post = Post(
            post_number=pd.post_number,
            handle_name=pd.handle_name,
            posted_at=pd.posted_at,
            likes=pd.likes,
            content=pd.content,
        )
        for url in pd.image_urls:
            post.images.append(Image(image_url=url))

        return post

    def _resolve_references(
        self, posts: list[Post], post_datas: list[PostData]
    ) -> PostReference:
        post_map = {post.post_number: post.id for post in posts}
        references = []
        for pd in post_datas:
            for ref_to_num in pd.ref_to_nums:
                if ref_to_num in post_map:
                    references.append(
                        PostReference(
                            from_post_id=post_map[pd.post_number],
                            to_post_id=post_map[ref_to_num],
                        )
                    )

        return references

    def _get_last_post_num(self, thread_id: int) -> int:
        result = select(func.max(Post.post_number)).where(Post.thread_id == thread_id)
        return result.scalar() or 0

    def _filter_new_posts(
        self, post_datas: list[PostData], last_post_num: int
    ) -> list[PostData]:
        [pd for pd in post_datas if pd.post_number > last_post_num]

    def _update_fts(self):
        pass
