from celery import shared_task
from celery.contrib.abortable import AbortableTask
from time import sleep
from flaskblog.models import *
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

@shared_task(bind=True, base=AbortableTask)
def like_post_task(self,user_id, public_id):
    post = Post.query.filter_by(public_id=public_id).first()
    cypher_query = """
        MATCH (post:Post {public_id: $public_id})
        SET post.love = $love_received,
            post.user_id = $user_id
        """
    graph.run(cypher_query, public_id=public_id, love_received=post.love, user_id=user_id)
    return "Like relationship added to the graph database."


@shared_task(bind=True, base=AbortableTask)
def delete_post_task(self, public_id):
    post = Post.query.filter_by(public_id=public_id).first()
    cypher_query = """
    MATCH (post:Post {public_id: $public_id})
    DETACH DELETE post
    """
    graph.run(cypher_query, public_id=post.public_id)

    return "Post deleted successfully."


@shared_task(bind=True, base=AbortableTask)
def topic_creation_task(self, creator_id):
    topic = Topic.query.filter_by(user_id=creator_id).order_by(Topic.date_created.desc()).first()
    topic_node = Node('Topic',id= topic.id, name=topic.name, 
    pub_id=topic.pub_id, date_created=topic.date_created,
    popular=topic.popular)
    graph.create(topic_node)
    
    creator = User.query.get(creator_id)
    if creator:
        user_node = Node('User', user_id=creator.id, user_name=creator.username, img_file=creator.image_file)
        graph.create(user_node)
        
        relationship = Relationship(user_node, 'CREATED', topic_node)
        graph.create(relationship)
    
    return 'Topic Created'


@shared_task(bind=True, base=AbortableTask)
def group_creation_task(self, creator_id, topic_id):
    creator = User.query.get(creator_id)
    
    topic = Topic.query.filter_by(id=topic_id).first()
    
    group = Groups.query.filter_by(topic_id=topic_id).order_by(Groups.date_posted.desc()).first()

    if creator and topic:
        user_node = Node('User', user_id=creator.id, user_name=creator.username, img_file=creator.image_file)
        graph.create(user_node)

        topic_node = Node('Topic', id=topic.id, name=topic.name, pub_id=topic.pub_id,
                          date_created=topic.date_created, popular=topic.popular)
        graph.create(topic_node)

        group_node = Node('Groups', id=group.id, content=group.content,
                          comments=group.comments, date_posted=group.date_posted)
        graph.create(group_node)

        user_group_relationship = Relationship(user_node, 'CREATED', group_node)
        graph.create(user_group_relationship)

        group_topic_relationship = Relationship(group_node, 'HAS_TOPIC', topic_node)
        graph.create(group_topic_relationship)

        return 'Group Created'

    return 'Invalid User or Topic'