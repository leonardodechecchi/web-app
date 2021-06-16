import itertools

from flask import render_template, url_for, redirect
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from wtforms import BooleanField

from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditProfileForm, ReservationForm, CreateCourse, AddEventCourse, \
    AddEventGym, CreateWeightRoom, CancelReservationForm
from app.models import User, Courses, requires_roles, WeightRooms, SchedulesCourse, SchedulesWeightRoom, Reservations


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')


@app.route('/about')
def about():
    return render_template('about-us.html', title='About Us')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # flash('You must logout to make a new registration', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # hashing password
        user = User(name=form.name.data, surname=form.surname.data, social_number=form.social_number.data,
                    email=form.email.data, password=hashed_pw, role='member')
        db.session.add(user)
        db.session.commit()
        # flash('Your account has been created! Now you are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # flash('You are already logged-in', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):  # if user exists and password is valid
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            pass
            # flash(f'Login Unsuccessful, please retry', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
@requires_roles('member')
def profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        user = User.query.filter_by(social_number=current_user.social_number).first()
        if form.name.data:
            user.name = form.name.data
        if form.surname.data:
            user.surname = form.surname.data
        if form.email.data:
            user.email = form.email.data
        if form.social_number.data:
            user.social_number = form.social_number.data
        if form.password.data:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_pw
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('profile.html', title='Profile', user=current_user, form=form)


@app.route('/dashboard')
@login_required
@requires_roles('instructor')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_weightrooms():
    turns = SchedulesWeightRoom.query.distinct(SchedulesWeightRoom.from_hour, SchedulesWeightRoom.to_hour).all()
    schedules = SchedulesWeightRoom.query.distinct(SchedulesWeightRoom.day).limit(7).all()
    allturns = SchedulesWeightRoom.query.all()
    weightrooms = WeightRooms.query.all()
    reservations = Reservations.query.with_entities(Reservations.schedule_weightroom_id,
                                                    func.count(Reservations.schedule_weightroom_id).label('count'))\
        .group_by(Reservations.schedule_weightroom_id).all()

    class F(ReservationForm):
        pass

    for allturn in allturns:
        setattr(F, str(allturn.id), BooleanField('Reserve Now'))
    form = F()

    if form.validate_on_submit():
        for allturn in allturns:
            if getattr(form, str(allturn.id)).data:
                reservation = Reservations(user_id=current_user.social_number, schedule_weightroom_id=allturn.id,
                                           schedule_course_id=None)
                db.session.add(reservation)
        db.session.commit()
        return redirect(url_for('calendar_reservations'))

    flag = {'flag': True}
    flag_slots = {'flag': True}
    return render_template('calendar_gym.html', title='Gym', schedules=schedules, turns=turns,
                           allturns=allturns, weightrooms=weightrooms, form=form, getattr=getattr, str=str, flag=flag,
                           reservations=reservations, flag_slots=flag_slots)


@app.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    turns = SchedulesCourse.query.distinct(SchedulesCourse.from_hour, SchedulesCourse.to_hour).all()
    schedules = SchedulesCourse.query.distinct(SchedulesCourse.day).limit(7).all()
    allturns = SchedulesCourse.query.all()
    courses = Courses.query.all()
    reservations = Reservations.query.with_entities(Reservations.schedule_course_id,
                                                    func.count(Reservations.schedule_course_id).label('count'))\
        .group_by(Reservations.schedule_course_id).all()

    class F(ReservationForm):
        pass

    for allturn in allturns:
        setattr(F, str(allturn.id), BooleanField('Reserve Now'))
    form = F()

    if form.validate_on_submit():
        for allturn in allturns:
            if getattr(form, str(allturn.id)).data:
                reservation = Reservations(user_id=current_user.social_number, schedule_weightroom_id=None,
                                           schedule_course_id=allturn.id)
                db.session.add(reservation)
        db.session.commit()
        return redirect(url_for('calendar_reservations'))

    flag = {'flag': True}
    flag_slots = {'flag': True}
    return render_template('calendar_courses.html', title='Courses', schedules=schedules, turns=turns,
                           allturns=allturns, courses=courses, form=form, str=str, getattr=getattr, flag=flag,
                           reservations=reservations, flag_slots=flag_slots)


@app.route('/calendar/reservations', methods=['GET', 'POST'])
@login_required
def calendar_reservations():
    reservations = Reservations.query.filter_by(user_id=current_user.social_number)
    courses = Courses.query.all()
    weightrooms = WeightRooms.query.all()
    reservation_courses = []
    reservation_weightroom = []
    for reservation in reservations:
        if reservation.schedule_course_id:
            reservation_courses.append(reservation.schedule_course_id)
        if reservation.schedule_weightroom_id:
            reservation_weightroom.append(reservation.schedule_weightroom_id)
    allturns_c = SchedulesCourse.query.filter(SchedulesCourse.id.in_(reservation_courses))
    allturns_w = SchedulesWeightRoom.query.filter(SchedulesWeightRoom.id.in_(reservation_weightroom))
    days_temp = []
    turns_temp = []
    for allturn_c in allturns_c:
        days_temp.append(allturn_c.day)
        turns_temp.append((allturn_c.from_hour, allturn_c.to_hour))
    for allturn_w in allturns_w:
        days_temp.append(allturn_w.day)
        turns_temp.append((allturn_w.from_hour, allturn_w.to_hour))
    days = list(dict.fromkeys(days_temp))
    turns = list(dict.fromkeys(turns_temp))
    days.sort()
    turns.sort()

    class F(CancelReservationForm):
        pass

    for allturn_c in allturns_c:
        setattr(F, str(allturn_c.id) + 'c', BooleanField('Cancel Reservation'))
    for allturn_w in allturns_w:
        setattr(F, str(allturn_w.id) + 'w', BooleanField('Cancel Reservation'))
    form = F()

    if form.validate_on_submit():  # TODO cancel reservation
        for allturn_c in allturns_c:
            if getattr(form, str(allturn_c.id) + 'c').data:
                print(allturn_c.day, allturn_c.from_hour, allturn_c.to_hour, "course")
        for allturn_w in allturns_w:
            if getattr(form, str(allturn_w.id) + 'w').data:
                print(allturn_w.day, allturn_w.from_hour, allturn_w.to_hour, "gym")

    flag = {'flag': True}
    return render_template('calendar_reservations.html', title='Reservations', days=days, turns=turns,
                           allturns_c=allturns_c, allturns_w=allturns_w, courses=courses, weightrooms=weightrooms,
                           flag=flag, zip=itertools.zip_longest, form=form, str=str, getattr=getattr)


@app.route('/calendar/instructor')
@login_required
@requires_roles('instructor')
def calendar_instructor():
    turns = SchedulesCourse.query.distinct(SchedulesCourse.from_hour, SchedulesCourse.to_hour).all()
    schedules = SchedulesCourse.query.distinct(SchedulesCourse.day).limit(7).all()
    courses = Courses.query.filter_by(instructor_id=current_user.social_number)
    allturns = SchedulesCourse.query.all()

    flag = {'flag': True}
    return render_template('calendar_instructor.html', title='Instructor', turns=turns, allturns=allturns,
                           schedules=schedules, courses=courses, flag=flag)


@app.route('/course/create', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def course_create():
    form = CreateCourse()
    if form.validate_on_submit():
        course = Courses(name=form.name.data, max_members=form.max_members.data)
        current_user.courses.append(course)
        db.session.add(course)
        db.session.commit()
        # flash(f'Courses {form.name.data} created successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('admin/create_course.html', form=form)


@app.route('/course/add-event', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def course_add_event():
    form = AddEventCourse()
    if form.validate_on_submit():
        course = Courses.query.filter_by(name=form.name.data).first()
        turn = SchedulesCourse.query.filter(SchedulesCourse.from_hour == form.turn_start.data,
                                            SchedulesCourse.to_hour == form.turn_end.data,
                                            SchedulesCourse.course_id == course.id,
                                            SchedulesCourse.day == form.date.data).first()
        if not turn:
            turn = SchedulesCourse(from_hour=form.turn_start.data, to_hour=form.turn_end.data, course_id=course.id,
                                   day=form.date.data)
            db.session.add(turn)
        db.session.commit()
        # flash(f'Successfully added an event to {form.name.data} class', 'success')
        return redirect(url_for('calendar_courses'))
    return render_template('admin/add_event.html', form=form)


@app.route('/weightroom/create', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def weightroom_create():
    weightroom = WeightRooms.query.first()
    form = CreateWeightRoom(obj=weightroom)
    if form.validate_on_submit():
        if not weightroom:
            weightroom = WeightRooms(max_members=form.max_members.data, dimension=form.dimension.data)
            db.session.add(weightroom)
        else:
            weightroom.max_members = form.max_members.data
            weightroom.dimension = form.dimension.data
        db.session.commit()
        # flash(f'Courses {form.name.data} created successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('admin/create_weightroom.html', form=form)


@app.route('/weightroom/add-event', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def weightroom_add_event():
    form = AddEventGym()
    if form.validate_on_submit():
        weightroom = WeightRooms.query.first()
        if not weightroom:
            return redirect(url_for('admin/create_weightroom'))
        turn = SchedulesWeightRoom.query.filter(SchedulesWeightRoom.from_hour == form.turn_start.data,
                                                SchedulesWeightRoom.to_hour == form.turn_end.data,
                                                SchedulesWeightRoom.weightroom_id == weightroom.id,
                                                SchedulesWeightRoom.day == form.date.data).first()
        if not turn:
            turn = SchedulesWeightRoom(from_hour=form.turn_start.data, to_hour=form.turn_end.data,
                                       weightroom_id=weightroom.id, day=form.date.data)
            db.session.add(turn)
        db.session.commit()
        # flash(f'Successfully added an event to {form.name.data} class', 'success')
        return redirect(url_for('calendar_weightrooms'))
    return render_template('admin/add_event_weightroom.html', form=form)
