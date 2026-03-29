from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from sqlalchemy.exc import IntegrityError
from app.models import User, Post, Comment
from app import db, content_detector

class LoginForm(FlaskForm):
    username = StringField('아이디', validators=[DataRequired()])
    password = PasswordField('비밀번호', validators=[DataRequired()])
    submit = SubmitField('로그인')

class RegistrationForm(FlaskForm):
    username = StringField('아이디', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('이메일', validators=[DataRequired(), Email()])
    password = PasswordField('비밀번호', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('비밀번호 확인', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('회원가입')

class PostForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    content = TextAreaField('내용', validators=[DataRequired()])
    submit = SubmitField('저장')

class CommentForm(FlaskForm):
    content = TextAreaField('댓글', validators=[DataRequired()])
    submit = SubmitField('작성')

def init_routes(app):
    @app.route("/")
    @app.route("/home")
    def home():
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
        return render_template('index.html', posts=posts)

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                hashed_password = generate_password_hash(form.password.data)
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password
                )
                db.session.add(user)
                db.session.commit()
                flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('이미 존재하는 아이디 또는 이메일입니다.', 'danger')
                
        return render_template('register.html', form=form)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            flash('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.', 'danger')
        return render_template('login.html', form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route("/post/new", methods=['GET', 'POST'])
    @login_required
    def new_post():
        form = PostForm()
        if form.validate_on_submit():
            is_toxic, result = content_detector.analyze_content(form.content.data)
            
            if is_toxic:
                categories = ", ".join(result.get("categories", []))
                flash(f'부적절한 내용이 감지되었습니다: {categories}', 'danger')
                return render_template('create_post.html', form=form)
            
            try:
                post = Post(
                    title=form.title.data,
                    content=form.content.data,
                    author=current_user
                )
                db.session.add(post)
                db.session.commit()
                flash('게시글이 작성되었습니다!', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                db.session.rollback()
                flash('게시글 작성 중 오류가 발생했습니다.', 'danger')
                print(f"Error: {str(e)}")
                
        return render_template('create_post.html', form=form)

    @app.route("/post/<int:post_id>", methods=['GET', 'POST'])
    def post(post_id):
        post = Post.query.get_or_404(post_id)
        form = CommentForm()
        
        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash('댓글을 작성하려면 로그인이 필요합니다.', 'danger')
                return redirect(url_for('login'))

            is_toxic, result = content_detector.analyze_content(form.content.data)
            
            if is_toxic:
                categories = ", ".join(result.get("categories", []))
                flash(f'부적절한 내용이 감지되었습니다: {categories}', 'danger')
            else:
                try:
                    comment = Comment(
                        content=form.content.data,
                        post=post,
                        author=current_user
                    )
                    db.session.add(comment)
                    db.session.commit()
                    flash('댓글이 작성되었습니다!', 'success')
                    return redirect(url_for('post', post_id=post.id))
                except Exception as e:
                    db.session.rollback()
                    flash('댓글 작성 중 오류가 발생했습니다.', 'danger')
                    print(f"Error: {str(e)}")
                    
        return render_template('post.html', post=post, form=form)

    @app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
    @login_required
    def update_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            flash('다른 사용자의 게시글은 수정할 수 없습니다.', 'danger')
            return redirect(url_for('post', post_id=post.id))

        form = PostForm()
        if form.validate_on_submit():
            is_toxic, result = content_detector.analyze_content(form.content.data)
            
            if is_toxic:
                categories = ", ".join(result.get("categories", []))
                flash(f'부적절한 내용이 감지되었습니다: {categories}', 'danger')
            else:
                try:
                    post.title = form.title.data
                    post.content = form.content.data
                    db.session.commit()
                    flash('게시글이 수정되었습니다!', 'success')
                    return redirect(url_for('post', post_id=post.id))
                except Exception as e:
                    db.session.rollback()
                    flash('게시글 수정 중 오류가 발생했습니다.', 'danger')
                    print(f"Error: {str(e)}")
                    
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
            
        return render_template('create_post.html', form=form, post=post)

    @app.route("/post/<int:post_id>/delete", methods=['POST'])
    @login_required
    def delete_post(post_id):
        try:
            post = Post.query.get_or_404(post_id)
            if post.author != current_user:
                flash('다른 사용자의 게시글은 삭제할 수 없습니다.', 'danger')
                return redirect(url_for('post', post_id=post.id))
                
            db.session.delete(post)
            db.session.commit()
            flash('게시글이 삭제되었습니다.', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('게시글 삭제 중 오류가 발생했습니다.', 'danger')
            print(f"Error: {str(e)}")
            return redirect(url_for('post', post_id=post_id))

    @app.route("/comment/<int:comment_id>/delete", methods=['POST'])
    @login_required
    def delete_comment(comment_id):
        try:
            comment = Comment.query.get_or_404(comment_id)
            if comment.author != current_user:
                flash('다른 사용자의 댓글은 삭제할 수 없습니다.', 'danger')
                return redirect(url_for('post', post_id=comment.post_id))
                
            post_id = comment.post_id
            db.session.delete(comment)
            db.session.commit()
            flash('댓글이 삭제되었습니다.', 'success')
            return redirect(url_for('post', post_id=post_id))
        except Exception as e:
            db.session.rollback()
            flash('댓글 삭제 중 오류가 발생했습니다.', 'danger')
            print(f"Error: {str(e)}")
            return redirect(url_for('post', post_id=comment.post_id))

    return app