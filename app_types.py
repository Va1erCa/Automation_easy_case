# Module for data types of the app

from datetime import datetime

from pgdb import Row, Rows


# The data structures for save in database
# Record in <category> table - product categories
class DBCategory(Row) :
    id: int                 # category id (primary key)
    category_name: str      # name of category

# Record in <discount> table - discounts applied in stores
class DBDiscount(Row) :
    id: int                 # discount id (primary key)
    value: float            # discount amount
    promo_action: str       # the name of the promotion for this discount

# Record in <goods> table - full list of goods of our chain stores
class DBGoods(Row) :
    #id: int                 # product ID - autoincrement field
    item_name: str          # name of the product
    category_id: int        # product category ID
    price: float            # retail price
    discount_id: int        # discount id
    purchase_price: float   # purchase price

# Record in <stuff> table - list of employees of our store chain
class DBStuff(Row) :
    #id: int                 # stuff ID - autoincrement field
    first_name: str         # employee's name
    middle_name: str        # employee's patronymic
    last_name: str          # employee's last name
    salary: int             # employee's salary
    phone: str              # employee's personal phone number


class DBPost(Row) :       # record in <post> table
    channel_id: int     # channel id  - part of the group primary key
    post_id: int     # post id      - part of the group primary key

    forward_from_chat : int | None    # channel id from where the post was forwarded (if any)
    creation_time: datetime     # post creation time
    drop_time: datetime | None    # time to delete a post
    is_advertising: bool    # the sign of an advertising post
    media_group_id: int      # media group id if the post is a group post
    media_type : str   # type of content
    post_text: str | None     # content of a text or a caption field if any
    text_len: int | None    # the length of the text content string
    text_entities_count: int | None     # the number of formatting entities in the text or caption field
    post_url: str |None     # the url-link to the post (for example, https://t.me/simulative_official/2109)
    is_planned: bool    # a sign that planning has been completed


class DBPostHist(Row) :       # record in <post_hist> table
    channel_id: int     # channel id  - part of the group foreign key
    post_id: int     # post id      - part of the group foreign key

    update_time: datetime   # update time
    observation_day: int    # serial number of the observation day
    post_comments: int     # number of comments
    post_views: int     # number of views
    stars: int     # number of <stars> reactions
    positives: int  # number of positive emoji
    negatives: int  # number of negative emoji
    neutrals: int   # number of neutrals emoji
    customs: int  # number of custom emoji
    reposts: int  # the number of reposts of this post


class DBMediaGroup(Row) :       # record in <post_hist> table
    media_group_id: int      # media group id if the post is a group post  - primary key

    update_time: datetime   # update time
    post_id: int     # post id
    observation_day: int    # serial number of the observation day
    post_order: int     # serial number of the post in the media group
    post_views: int     # number of views
    reposts: int    # the number of reposts of this post

class DBTaskPlan(Row) :       # record in <task_plan> table
    channel_id: int     # channel id  - part of the group foreign key
    post_id: int     # post id      - part of the group foreign key

    observation_day: int    # the ordinal number of the day on which the observation will be performed
    planned_at: datetime   # scheduled task start time
    # started_at: datetime | None  # the time when the task was actually started
    completed_at: datetime | None  # the time of the actual completion of the task