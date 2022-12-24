from flask import Flask, render_template, flash, redirect, url_for, request, abort, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


from app import app

from app.forms import LoginForm, RegistrationForm, ChapterForm, BookForm
from app.models import Reader, Author, Book, Chapter, Bookmark, Reader_book


@app.route('/')
@app.route('/novel')
def novel():
    if current_user.is_anonymous:
        book_lst = Book.get_all_books()
        if book_lst is None:
            book_lst = []
    elif session['role'] == 'auth':
        book_lst = Book.get_books_by_auth(current_user.id)
        if book_lst is None:
            book_lst = []
    else:
        book_lst = Book.get_all_books()
        if book_lst is None:
            book_lst = []
    return render_template('novel.html', title='Catalog', books=book_lst)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/novel")
    form = LoginForm()
    if form.validate_on_submit():
        if form.role.data:
            session['role'] = 'auth'
            user = Author.get_by_login(form.login.data)
        else:
            session['role'] = 'read'
            user = Reader.get_by_login(form.login.data)
        if user is None or not user.check_password(form.password.data):
            flash('invalid login or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('novel')
        return redirect(next_page)
    return render_template('login.html', title='Log In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('novel'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print('validate on')
        if form.role.data == True:
            user = Author(id=0,
                          login=form.login.data,
                          password_hash=None)
            user.set_password(form.password.data)
            if not Author.add(user):
                abort(500)
            flash('you registered')
            return redirect(url_for('login'))
        elif form.role.data == False:
            user = Reader(id=0,
                          login=form.login.data,
                          password_hash=None)
            user.set_password(form.password.data)
            if not Reader.add(user):
                abort(500)
            flash('you registered')
            return redirect(url_for('login'))
    return render_template('registration.html', title='Registration', form=form)


@app.route('/reader/<login>')
@login_required
def reader(login):
    user = Reader.get_by_login(login)
    books = Reader_book.get_books_by_reader_id(current_user.id)
    if books is None:
        books = []
    if user is None:
        abort(404)
    return render_template('reader.html', title=user.login, user=user, books=books)


@app.route('/author/<login>')
@login_required
def author(login):
    user = Author.get_by_login(login)
    books = Book.get_books_by_auth(current_user.id)
    if books is None:
        books = []
    if user is None:
        abort(404)
    return render_template('author.html', title=user.login, user=user, books=books)
    
@app.route('/book/<id>')
def book(id):
    if current_user.is_authenticated:
        book = Book.get_by_id(id)
        mark = Bookmark.get_mark_by_readbook_id(current_user.id, id)
        description = book.description
        descriptions = description.split('\\r\\n')
        if descriptions is None:
            descriptions = description
        print(mark)
        print(descriptions)
        return render_template('book.html', title=f"{book.name}", book=book, auth_id=book.auth_id, mark=mark, descriptions=descriptions,)
    else:
        book = Book.get_by_id(id)
        description = book.description
        descriptions = description.split('\\r\\n')
        if descriptions is None:
            descriptions = description
    return render_template('book.html', title=f"{book.name}", book=book, auth_id=book.auth_id, descriptions=descriptions)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(0,form.name.data,
                      form.description.data,
                      current_user.id)
        if not Book.add(book):
            abort(500)
        return redirect(url_for('novel'))
    return render_template('upload.html', title='upload', form=form)


@app.route('/chapload/<book_id>', methods=['GET', 'POST'])
def chapter_upload(book_id):
    form = ChapterForm()
    if form.validate_on_submit():
        chapter = Chapter(0, form.num_ch.data,
                             form.content.data,
                             book_id)
        chapter_id = Chapter.add(chapter)
        if chapter_id is None:
            abort(500)
        chapter.id = chapter_id
        return redirect(url_for('ch_book', id=chapter.id))
    return render_template('chapload.html', title='Chapter', form=form)


@app.route('/chapter/<id>', methods=['GET'])
def ch_book(id):
    print(id)
    chapter = Chapter.get_by_id(id)
    content = chapter.content
    contents = content.split('\\r\\n')
    print(content)
    print(contents)
    return render_template('chapter.html', chapter=chapter, contents=contents)


@app.route('/book_chapters/<book_id>')
def book_chapters(book_id):
    chapters = Chapter.get_all_by_book_id(book_id)
    print(book_id)
    return render_template('chapters.html', title='chapters', chapters=chapters, book_id=book_id)
    

@app.route('/bookmarks') 
@login_required
def bookmarks():
    user = Reader.get_by_id(current_user.id)
    books = Reader_book.get_books_by_reader_id(current_user.id)
    if books is None:
        books = []
    if user is None:
        abort(404)
    return render_template('bookmarks.html', title='bookmarks', books=books)
    

@app.route('/add_bookmark/<chapter_id>')
def add_bookmark(chapter_id):
    read_id = current_user.id
    if not Bookmark.delete_by_chapter_id(chapter_id, read_id):
        abort(500)
    chapter = Chapter.get_by_id(chapter_id)
    book_id = chapter.book_id
    bookmark = Bookmark(0, read_id, 
                           book_id,
                           chapter_id)
    bookmark_id = Bookmark.add_bookmark(bookmark)
    read_book = Reader_book.add_read_book(read_id, book_id)
    if bookmark_id is None:
        abort(500)
    bookmark.id = bookmark_id
    return redirect(url_for('ch_book', id=chapter_id)), read_book
