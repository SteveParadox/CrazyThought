from celery import shared_task
from celery.contrib.abortable import AbortableTask
from time import sleep
from flaskblog.models import Post, User
from py2neo import Graph, Node, Relationship
from flaskblog import graph
from flaskblog.main.form import PostForm
from flask_login import current_user


@shared_task(bind=True, base=AbortableTask)
def data_task(self):
    posts = Post.query.order_by(Post.content.desc()).all()
    print("Number of posts:", len(posts)) 
    for post in posts:
        post_node = Node('Post', id=post.id, content=post.content, 
        comments=post.comments, love=post.love,
                         public_id=post.public_id, viewed=post.viewed, 
                         date_posted=post.date_posted)
        graph.create(post_node)
        user = User.query.get(post.user_id)
        if user:
            user_node = Node('User', user_id=user.id, user_name=user.username,
             img_file=user.image_file ) 
            graph.create(user_node)
            relationship = Relationship(user_node, 'POSTED', post_node)
            graph.create(relationship)
        else:

            print(f"User with user_id={post.user_id} not found")
    return "Data added to the graph database."

@shared_task(bind=True, base=AbortableTask)
def create_post_task(self, user_id):
    post = Post.query.filter_by(user_id=user_id).order_by(Post.date_posted.desc()).first()
    post_node = Node('Post', id=post.id, content=post.content, 
        comments=post.comments, love=post.love,
                         public_id=post.public_id, viewed=post.viewed, 
                         date_posted=post.date_posted)
    graph.create(post_node)
    user = User.query.get(post.user_id)
    if user:
        user_node = Node('User', user_id=user.id, user_name=user.username,
            img_file=user.image_file ) 
        graph.create(user_node)
        relationship = Relationship(user_node, 'POSTED', post_node)
        graph.create(relationship)
    return 'Added'

