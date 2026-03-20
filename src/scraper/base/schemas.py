from dataclasses import dataclass
from datetime import datetime


@dataclass
class ThreadData:
    title: str
    url: str
    created_at: datetime


@dataclass
class PostData:
    post_number: int
    handle_name: str
    posted_at: datetime
    likes: int
    content: str
    image_urls: list[str]
    ref_to_nums: list[int]
