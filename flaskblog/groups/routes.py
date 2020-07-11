from operator import itemgetter
from flask import Blueprint, render_template, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from flaskblog import db, request, abort
from flaskblog.groups.forms import GroupPostForm, SearchPostForm, CommentForm
from flaskblog.models import Groups, Topic, TopicSchema, Group_comment

groups = Blueprint('groups', __name__)


@groups.route('/topics', methods=['POST', 'GET'])
def topics():
    topic = Topic.query.order_by(Topic.date_created.desc()).paginate()

    form = SearchPostForm()
    results = Topic.query.all()
    topics_schema = TopicSchema(many=True)
    res = topics_schema.dump(results)
    result = list(map(itemgetter('name'), res))
    paxx = form.content.data
    if paxx in result:
        return render_template('search.html', form=form, paxx=paxx)

    return render_template('topics.html', topic=topic, form=form)


@groups.route("/topics/conversation/<int:topics_id>/<string:topics_name>", methods=['POST', 'GET'])
def conversation(topics_id, topics_name):
    topics = Topic.query.get_or_404(topics_id, topics_name)
    form = GroupPostForm()

    if form.validate_on_submit():
        post = Groups(content=form.content.data, group=current_user, topic_id=topics.id)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('groups.conversation', topics_id=topics.id, topics_name=topics.name))

    page = request.args.get('page', 1, type=int)
    posts = Groups.query.filter_by(topic_id=topics.id).order_by(Groups.date_posted.desc()).paginate(page=page,
                                                                                                    per_page=50)

    return render_template('convo.html', topics_id=topics.id, posts=posts, form=form, topics=topics,
                           topics_name=topics.name)


@groups.route("/topics/conversation/<int:topics_id>/<string:topics_name>/<int:groups_id>", methods=['POST', 'GET'])
def discussion(topics_id, topics_name, groups_id):
    topics = Topic.query.get_or_404(topics_id, topics_name)
    groups = Groups.query.get_or_404(groups_id)
    post = Groups.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Group_comment(message=form.message.data, groups_id=groups.id, disc=current_user)
        db.session.add(comment)
        groups.comments = groups.comments + 1
        db.session.commit()
        return redirect(request.url)
    gc = Group_comment.query.filter_by(groups_id=groups.id).order_by(Group_comment.pub_date.desc()).paginate()

    return render_template('discussion.html', groups_id=groups.id, post=post,
                           groups=groups, topics_id=topics.id,
                           topics_name=topics.name, topics=topics, form=form, gc=gc)


@groups.route("/topics/conversation/<int:topics_id>/<string:topics_name>/<int:groups_id>/comment/<int:gc_id>/delete",
              methods=['POST', 'GET'])
def delete_discussion(topics_id, topics_name, groups_id, gc_id):
    topics = Topic.query.get_or_404(topics_id, topics_name)
    groups = Groups.query.get_or_404(groups_id)
    gc = Group_comment.query.get_or_404(gc_id)
    if gc.disc != current_user:
        abort(403)
    db.session.delete(gc)
    groups.comments = groups.comments - 1
    db.session.commit()
    return redirect(url_for('groups.discussion', groups_id=groups.id,
                            groups=groups, topics_id=topics.id,
                            topics_name=topics.name, topics=topics, gc=gc))
