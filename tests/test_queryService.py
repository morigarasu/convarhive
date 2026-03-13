from setup_test import setup_test_db
from services import Query, PostOrder


# def test_query_search():
# def test_query_thread():
def test_query_post():
    SessionLocal = setup_test_db(echo=False)

    with SessionLocal() as session:
        query_srvs = Query(session)

        posts_thread1 = query_srvs.get_posts_by_thread_id(1)
        post1_replies = query_srvs.get_replies(1)
        # query_srvs.get_referenced_posts()
        post1 = query_srvs.get_post_by_thread_and_postnum(1, 1)
        posts_list = query_srvs.get_list_posts(1, 10, 1, PostOrder.REFED)

        assert len(posts_thread1) == 3
        assert len(post1_replies) == 2

        assert posts_thread1[0].content == "これはテスト投稿です"
        assert post1_replies[0].content == ">>1 それな"

        assert post1.id == 1
        assert posts_list[0].id == 1
