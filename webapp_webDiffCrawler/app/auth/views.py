from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from webapp_webDiffCrawler.app.main import main
from webapp_webDiffCrawler.app.models import Users, Configurations
from webapp_webDiffCrawler.app import dbSession
from .forms import LoginForm, RegistrationForm, SecretTokenGenrationForm
import datetime


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


@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def adminpage():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))

    configurationRow = dbSession.query(Configurations).first()

    if configurationRow is None:
        abort(404)

    configurationDict = {}
    configurationDict['beginhour'] = configurationRow.dailyschedulebegin.hour
    configurationDict['beginminute'] = configurationRow.dailyschedulebegin.minute
    configurationDict['endhour'] = configurationRow.dailyscheduleend.hour
    configurationDict['endminute'] = configurationRow.dailyscheduleend.minute

    if (configurationRow.runmode == 0):
        configurationDict['differentstatus'] = "on"
    else:
        configurationDict['differentstatus'] = "off"

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
        return redirect(url_for('auth.adminpage'))

    users = []
    for user in dbSession.query(Users).order_by(Users.id_users.desc()):
        currUser = dict()
        currUser['id_users'] = user.id_users
        currUser['email'] = user.email
        currUser['username'] = user.username
        currUser['id_roles'] = user.id_roles
        currUser['secrettoken'] = user.secrettoken

        users.append(currUser)

    return render_template('auth/admin.html', secretTokenForm=form, users=users, configuration=configurationDict)

@auth.route('/updateschedule', methods=['POST'])
@login_required
def updateschedule():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))

    configurationRow = dbSession.query(Configurations).first()

    if configurationRow is None:
        abort(404)

    currDatetime = datetime.datetime.now()

    newDailyschedulebegin = datetime.datetime(year=currDatetime.year, month=currDatetime.month, day=currDatetime.day, hour=int(request.form['beginhour']), minute=int(request.form['beginminute']))
    newDailyscheduleend = datetime.datetime(year=currDatetime.year, month=currDatetime.month, day=currDatetime.day, hour=int(request.form['endhour']), minute=int(request.form['endminute']))

    configurationRow.dailyschedulebegin = newDailyschedulebegin
    configurationRow.dailyscheduleend = newDailyscheduleend

    dbSession.add(configurationRow)
    dbSession.commit()
    flash('Crawling schedule updated to ' + str(configurationRow.dailyschedulebegin) + " --- " + str(configurationRow.dailyscheduleend))

    return redirect(url_for('auth.adminpage'))


@auth.route('/togglecrawler', methods=['POST'])
@login_required
def togglecrawler():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))

    flashMessage = ""

    configurationRow = dbSession.query(Configurations).first()

    if configurationRow is None:
        abort(404)

    if configurationRow.runmode == 0:
        configurationRow.runmode = 1
        flashMessage = "The scraper is now active!"
    else:
        configurationRow.runmode = 0
        flashMessage = "The scraper has been deactivated!"

    dbSession.add(configurationRow)
    dbSession.commit()
    flash(flashMessage)

    return redirect(url_for('auth.adminpage'))


@auth.route('/deleteauser', methods=['POST'])
@login_required
def deleteAUser():
    if current_user.id_roles != 1: # If not an admin
        return redirect(url_for('main.index'))
    userId = request.form['deleteUserId']
    userToDelete = dbSession.query(Users).filter_by(id_users=userId).first()
    dbSession.delete(userToDelete)
    dbSession.commit()
    return redirect(url_for('auth.adminpage'))


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

    return redirect(url_for('auth.adminpage'))