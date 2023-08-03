from operator import itemgetter
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.exceptions import abort
from sqlalchemy import desc
from datetime import datetime, timedelta

from flaskblog import db
from flaskblog.groups.forms import GroupPostForm, SearchPostForm, CommentForm
from flaskblog.models import Groups, Topic, TopicSchema, Group_comment, GroupReplyComment
from flaskblog.users.decorator import check_confirmed

groups = Blueprint('groups', __name__)


@groups.route('/mygroups')
@login_required
def my_groups():
    groups = Groups.query.filter_by(group=current_user).all()
    groups_schema = GroupSchema(many=True)
    res = groups_schema.dump(groups)
    return jsonify(res)


@groups.route('/topics', methods=['GET'])
def topics():
    form = SearchPostForm()
    topics = Topic.query.filter(Topic.date_created >= (datetime.now() - timedelta(days=47))).order_by(
        desc(Topic.date_created)).paginate()
    topics_schema = TopicSchema(many=True)
    res = topics_schema.dump(topics.items)
    result = list(map(itemgetter('name'), res))
    paxx = request.args.get('text')
    if paxx in result:
        return jsonify(result)
    return jsonify(res)


@groups.route('/topics/search', methods=['POST'])
def topic_search():
    data = request.form.get('text')
    results = Topic.query.filter(Topic.name.ilike(f"%{data}%")).all()
    if not results:
        return jsonify("No Result")
    topic_schema = TopicSchema(many=True)
    res = topic_schema.dump(results)
    return jsonify(res)


@groups.route('/popular/topics')
def popular_topics():
    topics = Topic.query.order_by(desc(Topic.popular)).all()
    topics_schema = TopicSchema(many=True)
    res = topics_schema.dump(topics)
    return jsonify(res)


@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>", methods=['POST', 'GET'])
def conversation(pub_id, topics_name):
    topic = Topic.query.filter_by(pub_id=pub_id, name=topics_name).first_or_404()
    form = GroupPostForm()
    if form.validate_on_submit():
        post = Groups(content=form.content.data, group=current_user, topic_id=topic.id)
        db.session.add(post)
        db.session.commit()

        return jsonify({"message": "Post added successfully!"}), 201

    page = request.args.get('page', 1, type=int)
    posts = Groups.query.filter_by(topic_id=topic.id).order_by(desc(Groups.date_posted)).paginate(page=page,
                                                                                                   per_page=50)
    posts_schema = GroupSchema(many=True)
    res = posts_schema.dump(posts.items)

    return jsonify({
        "pub_id": topic.pub_id,
        "posts": res,
        "topics": topic.name
    })


@groups.route("/topics/conversation/my_conversation/<string:pub_id>/<string:topics_name>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def my_conversation(pub_id, topics_name):
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    posts = Groups.query.filter_by(topic_id=topics.id).filter_by(group=current_user).order_by(
        Groups.date_posted.desc()).all()

    return jsonify({"pub_id": topics.pub_id, "posts": [post.serialize for post in posts], "topics": topics.serialize, "topics_name": topics.name})


@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>/<int:groups_id>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def discussion(pub_id, topics_name, groups_id):
    page = request.args.get('page', 1, type=int)
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    groups = Groups.query.get_or_404(groups_id)
    post = Groups.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Group_comment(message=form.message.data, groups_id=groups.id, disc=current_user)
        db.session.add(comment)
        groups.comments = groups.comments + 1
        db.session.commit()
        return redirect(request.url)
    gc = Group_comment.query.filter_by(groups_id=groups.id).order_by(Group_comment.pub_date.desc()).paginate(page=page,
                                                                                                             per_page=20)

    return jsonify({"groups_id": groups.id, "post": [p.serialize for p in post], "groups": groups.serialize, "pub_id": topics.pub_id,
                           "topics_name": topics.name, "topics": topics.serialize, "form": form.serialize, "gc": [c.serialize for c in gc.items]})

@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>/<int:groups_id>/comment/<int:gc_id>",
              methods=['POST', 'GET'])
@login_required
@check_confirmed
def reply_discussion(pub_id, topics_name, groups_id, gc_id):
    page = request.args.get('page', 1, type=int)
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    groups = Groups.query.get_or_404(groups_id)
    comment = Group_comment.query.filter_by(id=gc_id).first()
    rc = GroupReplyComment.query.filter_by(group_comment=comment.id).order_by(
        GroupReplyComment.pub_date.desc()).paginate(page=page, per_page=20)
    form = CommentForm()
    if form.validate_on_submit():
        rc = GroupReplyComment(message=form.message.data, g_reply=current_user, group_comment=comment.id)
        db.session.add(rc)
        comment.replys = comment.replys + 1
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400

@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>/<int:groups_id>/delete",
              methods=['POST', 'GET'])
@login_required
@check_confirmed
def delete_group(pub_id, topics_name, groups_id):
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    groups = Groups.query.get_or_404(groups_id)
    gc = Group_comment.query.filter_by(groups_id=groups.id).all()
    for x in gc:
        comment = Group_comment.query.filter_by(id=x.id).all()
        for z in comment:
            rc = GroupReplyComment.query.filter_by(group_comment=z.id).all()
            for i in rc:
                db.session.delete(i)
                db.session.commit()
    if groups.group != current_user:
        abort(403)

    for o in gc:
        db.session.delete(o)
    db.session.delete(groups)
    db.session.commit()
    return jsonify({'success': True}), 200

@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>/<int:groups_id>/comment/<int:gc_id>/delete",
              methods=['POST', 'GET'])
@login_required
@check_confirmed
def delete_discussion(pub_id, topics_name, groups_id, gc_id):
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    groups = Groups.query.get_or_404(groups_id)
    gc = Group_comment.query.get_or_404(gc_id)
    comment = Group_comment.query.filter_by(id=gc.id).all()
    for z in comment:
        rc = GroupReplyComment.query.filter_by(group_comment=z.id).all()
        for i in rc:
            db.session.delete(i)
            db.session.commit()
    if gc.disc != current_user:
        abort(403)
    db.session.delete(gc)
    groups.comments = groups.comments - 1
    db.session.commit()
    return jsonify({'success': True}), 200
