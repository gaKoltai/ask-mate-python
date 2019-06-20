from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager
import util

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = connection.UPLOAD_FOLDER


@app.route('/', methods = ['POST', 'GET'])
def route_index():

    latest_questions = data_manager.get_latest_questions()

    return render_template('list.html', user_questions=latest_questions)


@app.route('/list', methods = ['POST', 'GET'])
def route_questions():
    if request.method == 'GET':
        user_questions = data_manager.get_data_from_db('question', request.args.get('order_by'), request.args.get('order_direction'))
        return render_template('list.html',
                               user_questions =user_questions,
                               order_by=request.args.get('order_by'),
                               order_direction=request.args.get('order_direction'))

    if request.method == 'POST':
        return redirect(url_for('route_questions', order_by=request.form['order_by'],
                                order_direction = request.form['order_direction']))


@app.route('/question/<question_id>')
def route_question_with_answer(question_id=None):
    if request.args.get('view_number_increment'):
        data_manager.increment_view_number(item_id=question_id)
    if question_id is not None:
        tags = data_manager.get_question_tags(question_id)
        question = data_manager.get_question_by_id(question_id=question_id)
        answers = data_manager.get_answers_by_question_id(question_id=question_id)
        question_comments = data_manager.get_comment_by_question_id(question_id=question_id)
        if len(answers) != 0:
            answer_ids = tuple(data_manager.get_answer_ids_by_answers(answers))
            answer_comments = data_manager.get_comments_by_answer_id(answer_ids=answer_ids)
        else:
            answer_comments = None

    return render_template('question_with_answers.html',
                           tags = tags,
                           question=question,
                           question_id=question_id,
                           answers=answers,
                           question_comments=question_comments,
                           answer_comments=answer_comments)


@app.route('/add-question', methods=['GET', 'POST'])
def route_ask_new_question():

    if request.method == 'POST':

        util.upload_file(request.files['image'])

        new_question = data_manager.add_question(request.form, request.files['image'].filename)
        data_manager.add_question_to_db(new_question)

        return redirect('/')

    return render_template('new_question.html')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):

    question = data_manager.get_question_by_id(question_id=question_id)

    if request.method == 'POST':

        edited_info = request.form

        data_manager.edit_question(edited_info, question_id)

        return redirect(url_for('route_question_with_answer', question_id=question_id))

    return render_template('edit_question.html', question=question, question_id=question_id)


@app.route('/question/<question_id>/<vote>')
@app.route('/question/<question_id>/<vote>/<answer_id>')
def route_vote(vote= None,question_id = None, answer_id = None ):
    if answer_id:
        data_manager.vote_answer(vote, answer_id)
        return redirect(url_for('route_question_with_answer', question_id=question_id))
    else:
        data_manager.vote_question(vote, question_id)
        return redirect(url_for('route_questions',
                                order_by=request.args.get('order_by'),
                                order_directuion=request.args.get('order_direction')))


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id=None):
    if request.method == 'POST':

        answer = request.form.get('answer')

        util.upload_file(request.files['image'])
        data_manager.add_answer(question_id=question_id, answer=answer, image_name=request.files['image'].filename)

        return redirect(url_for('route_question_with_answer', question_id=question_id))

    question = data_manager.get_question_by_id(question_id=question_id)
    return render_template('add_answer.html', question=question, question_id=question_id)


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.delete_answer_by_answer_id(answer_id)
    return redirect(url_for('route_question_with_answer', question_id=question_id))


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id=None):
    data_manager.delete_question(question_id)
    return redirect(url_for('route_questions'))


@app.route('/search')
def route_search():

    search_phrase = request.args.get('search')
    questions = data_manager.search_questions(search_phrase)
    data_manager.search_highlights(search_phrase,questions)

    return render_template('search.html', user_questions=questions)


@app.route('/question/<question_id>/new-comment', methods=['GET','POST'])
def route_new_question_comment(question_id=None):
    if request.method == 'POST':
        comment = request.form.get('question_comment')
        data_manager.add_comment_to_question(question_id=question_id, comment_message=comment)
        return redirect(url_for('route_question_with_answer', question_id=question_id))

    question = data_manager.get_question_by_id(question_id=question_id)
    return render_template('add_comment.html', question=question)


@app.route('/answer/<answer_id>/new-comment', methods=['GET','POST'])
def route_new_answer_comment(answer_id=None):
    if request.method == 'POST':
        comment = request.form.get('answer_comment')
        data_manager.add_comment_to_answer(answer_id=answer_id, comment_message=comment)
        question_id = data_manager.get_question_id_by_answer_id(answer_id=answer_id)
        return redirect(url_for('route_question_with_answer', question_id=question_id))

    answer = data_manager.get_answer_by_id(answer_id=answer_id)
    return render_template('add_comment.html', answer=answer)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def route_add_tags(question_id):
    if request.method == "POST":
        data_manager.new_tag(request.form['tag_name'])

    question_tags = data_manager.get_question_tags(question_id)
    rest_of_tags = data_manager.get_rest_of_tags(question_id)
    return render_template('add_tag.html', question_id=question_id,
                           question_tags= question_tags,
                           rest_of_tags = rest_of_tags)


@app.route('/question/<question_id>/add_tag/<tag_id>')
def route_add_tag(question_id, tag_id):
    data_manager.add_tag(question_id, tag_id)
    return redirect((url_for('route_add_tags', question_id=question_id)))


@app.route('/question/<question_id>/remove_tag/<tag_id>')
def route_remove_tag(question_id, tag_id):
    data_manager.remove_tag(question_id, tag_id)
    where_to_redirect = request.args.get('where_to_redirect')
    return redirect((url_for(where_to_redirect, question_id=question_id)))


@app.route('/comments/<comment_id>/delete')
def route_delete_comment(comment_id=None):
    ids = data_manager.get_ids_by_comment_id(comment_id=comment_id)
    if ids['question_id'] is not None:
        question_id = ids['question_id']
    else:
        question_id = data_manager.get_question_id_by_answer_id(ids['answer_id'])

    if comment_id:
        data_manager.delete_from_table(table='comment', parameter='id', value=comment_id)
    return redirect(url_for('route_question_with_answer', question_id=question_id))


@app.route('/comments/<comment_id>/edit', methods=['GET', 'POST'])
def route_edit_comment(comment_id=None):
    if request.method == 'POST':
        new_message = request.form.get('message')
        data_manager.update_comment_by_comment_id(comment_id=comment_id, message=new_message)
        ids = data_manager.get_ids_by_comment_id(comment_id=comment_id)
        if ids['question_id'] is not None:
            question_id = ids['question_id']
        else:
            question_id = data_manager.get_question_id_by_answer_id(ids['answer_id'])
        return redirect(url_for('route_question_with_answer', question_id=question_id))

    comment = data_manager.get_comment_by_comment_id(comment_id)
    return render_template('edit_comment.html', comment=comment)


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(answer_id):

    answer = data_manager.get_answer_by_id(answer_id)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)

    if request.method == 'POST':

        edited_answer = request.form

        data_manager.edit_answer(answer_id, edited_answer)

        return redirect(url_for('route_question_with_answer', question_id=question_id))

    return render_template('edit_answer.html', answer=answer )


@app.route('/commit/<comment_id>/delete-force')
def route_delete_force(comment_id=None):
    comment = data_manager.get_comment_by_comment_id(comment_id=comment_id)
    return render_template('delete.html', comment=comment)


@app.route('/comments/<comment_id>/dont-delete')
def route_dont_delete_comment(comment_id=None):
    ids = data_manager.get_ids_by_comment_id(comment_id=comment_id)
    if ids['question_id'] is not None:
        question_id = ids['question_id']
    else:
        question_id = data_manager.get_question_id_by_answer_id(ids['answer_id'])
    return redirect(url_for('route_question_with_answer', question_id=question_id))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )