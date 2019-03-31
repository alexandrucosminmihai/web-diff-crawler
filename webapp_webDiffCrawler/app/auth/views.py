from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from webapp_webDiffCrawler.app.main import main
from webapp_webDiffCrawler.app.models import Users
from webapp_webDiffCrawler.app import dbSession
from .forms import LoginForm, RegistrationForm, SecretTokenGenrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in')
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbSession.query(Users).filter(Users.email==form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.rememberMe.data)
            next = request.args.get('next') # Where the user wants to go next
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password', 'error')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("main.index"))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in')
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = dbSession.query(Users).filter(Users.secrettoken==form.secrettoken.data).first()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data

        dbSession.add(user)
        dbSession.commit()
        flash('You can now log in')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/users', methods=['GET', 'POST'])
@login_required
def manageusers():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))

    form = SecretTokenGenrationForm()
    if form.validate_on_submit():
        # Create a new user entry in order to get its id_users generated
        user = Users()
        dbSession.add(user)
        dbSession.commit()

        # Generate the secret token for this user
        user.secrettoken = user.generateToken()
        if form.isAdmin.data:
            user.id_roles = 1
        dbSession.add(user)
        dbSession.commit()
        flash('New secret token generated. A person can now register using it.')
        return redirect(url_for('auth.manageusers'))

    users = []
    for user in dbSession.query(Users).order_by(Users.id_users.desc()):
        currUser = dict()
        currUser['id_users'] = user.id_users
        currUser['email'] = user.email
        currUser['username'] = user.username
        currUser['id_roles'] = user.id_roles
        currUser['secrettoken'] = user.secrettoken

        users.append(currUser)

    return render_template('auth/users.html', secretTokenForm=form, users=users)

@auth.route('/deleteauser', methods=['POST'])
@login_required
def deleteAUser():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))
    userId = request.form['deleteUserId']
    userToDelete = dbSession.query(Users).filter_by(id_users=userId).first()
    dbSession.delete(userToDelete)
    dbSession.commit()
    return redirect(url_for('auth.manageusers'))


@auth.route('/deleteusers', methods=['POST'])
@login_required
def deleteUsers():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))

    idsToDelete = request.form.getlist('delete_checkbox')
    if idsToDelete:
        for userId in idsToDelete:
            userToDelete = dbSession.query(Users).filter_by(id_users=userId).first()
            dbSession.delete(userToDelete)

        dbSession.commit()

    return redirect(url_for('auth.manageusers'))