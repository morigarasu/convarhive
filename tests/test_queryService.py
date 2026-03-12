from setup_test_db import setup_test_db
from services import Query


# def test_query_search():
# def test_query_thread():
def test_query_post():
    SessionLocal = setup_test_db()

    with SessionLocal() as session:
        query_serv = Query(session)

        posts_thread1 = query_serv.get_posts_by_thread_id(1)
        print("Get replies")
        post1_replies = query_serv.get_replies(1)
        """
        query_serv.get_referenced_posts()
        query_serv.get_post_by_num()
        """

        assert len(posts_thread1) == 3
        assert len(post1_replies) == 2

        assert posts_thread1[0].content == "これはテスト投稿です"
        assert post1_replies[0].content == ">>1 それな"
