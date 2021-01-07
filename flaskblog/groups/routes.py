from operator import itemgetter
from flask import Blueprint, render_template, url_for, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import redirect
from flaskblog import db, request, abort, flash
from flaskblog.groups.forms import GroupPostForm, SearchPostForm, CommentForm
from flaskblog.models import Groups, Topic, TopicSchema, Group_comment, GroupReplyComment
from flaskblog.users.decorator import check_confirmed
import datetime

groups = Blueprint('groups', __name__)


@groups.route('/mygroups')
def my_groups():
    groups = Groups.query.filter_by(group=current_user).all()
    return render_template('my_groups.html', groups=groups)


@groups.route('/topics', methods=['POST', 'GET'])
def topics():
    form = SearchPostForm()
    topic = Topic.query.filter(Topic.date_created >= (datetime.datetime.now() - datetime.timedelta(days=47))).order_by(
        Topic.date_created.desc()).paginate()
    results = Topic.query.all()
    topics_schema = TopicSchema(many=True)
    res = topics_schema.dump(results)
    result = list(map(itemgetter('name'), res))
    paxx = form.content.data
    if paxx in result:
        return render_template('search.html', form=form, paxx=paxx)

    return render_template('topics.html', topic=topic, form=form)


@groups.route('/topics/search', methods=['POST'])
def topic_search():
    data = request.form.get('text')
    results = Topic.query.all()
    re =[]
    for i in results:
        if len(data) > 0:
            if str(data[0]).upper() in i.name or str(data[0]).lower() in i.name:
                print(i.name)
                rest = Topic.query.filter_by(name=i.name).all()
                topic_schema = TopicSchema(many=True)
                res = topic_schema.dump(rest)
                re.append(res)
                return jsonify(res)
            else:
                res = 'No Result'
                return jsonify(res)

        else:
            res = 'No Result'
            return jsonify(res)
    return jsonify({
        "res": 'no result'
    })


@groups.route('/popular/topics')
def popular_topics():
    topics = Topic.query.order_by(Topic.popular.desc()).all()
    return render_template('', topics=topics)


@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>", methods=['POST', 'GET'])
def conversation(pub_id, topics_name):
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    topics.popular = topics.popular + 1
    db.session.commit()
    form = GroupPostForm()
    if form.validate_on_submit():
        post = Groups(content=form.content.data, group=current_user, topic_id=topics.id)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('groups.conversation', pub_id=topics.pub_id, topics_name=topics.name))

    page = request.args.get('page', 1, type=int)
    posts = Groups.query.filter_by(topic_id=topics.id).order_by(Groups.date_posted.desc()).paginate(page=page,
                                                                                                    per_page=50)

    return render_template('convo.html', pub_id=topics.pub_id, posts=posts, form=form, topics=topics,
                           topics_name=topics.name)


@groups.route("/topics/conversation/my_conversation/<string:pub_id>/<string:topics_name>", methods=['POST', 'GET'])
@login_required
@check_confirmed
def my_conversation(pub_id, topics_name):
    topics = Topic.query.filter_by(pub_id=pub_id).first()
    posts = Groups.query.filter_by(topic_id=topics.id).filter_by(group=current_user).order_by(
        Groups.date_posted.desc()).all()

    return render_template('my_convo.html', pub_id=topics.pub_id, posts=posts, topics=topics,
                           topics_name=topics.name)


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

    return render_template('discussion.html', groups_id=groups.id, post=post,
                           groups=groups, pub_id=topics.pub_id,
                           topics_name=topics.name, topics=topics, form=form, gc=gc)


@groups.route("/topics/conversation/<string:pub_id>/<string:topics_name>/<int:groups_id>/comment/<int:gc_id>",
              methods=['POST', 'GET'])
@login_required
@check_confirmed
def reply_discussion(pub_id, topics_name, groups_id, gc_id):
    # data= request.form.get('text')

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
        return redirect(url_for('groups.reply_discussion', pub_id=topics.pub_id, groups_id=groups.id, gc_id=comment.id,
                                topics_name=topics.name))
    return render_template('group_discussion.html', groups_id=groups.id,
                           groups=groups, pub_id=topics.pub_id,
                           topics_name=topics.name, topics=topics, form=form, rc=rc, comment=comment)


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
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('groups.conversation', pub_id=topics.pub_id, topics_name=topics.name))


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
    return redirect(url_for('groups.discussion', groups_id=groups.id,
                            groups=groups, pub_id=topics.pub_id,
                            topics_name=topics.name, topics=topics, gc=gc))
