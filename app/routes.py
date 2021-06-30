from datetime import datetime

from flask import render_template, url_for, redirect, flash
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import BooleanField, SubmitField

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
        flash('You must logout to make a new registration', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # hashing password
        user = User(name=form.name.data, surname=form.surname.data, social_number=form.social_number.data,
                    email=form.email.data, password=hashed_pw, role='member')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Now you are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged-in', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):  # if user exists and password is valid
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful, please retry', 'danger')
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
        flash('Profile has been successfully edited', 'success')
        return redirect(url_for('home'))
    return render_template('profile.html', title='Profile', user=current_user, form=form)


@app.route('/dashboard')
@login_required
@requires_roles('instructor')
def dashboard():  # TODO add delete course and delete scheduling
    return render_template('dashboard.html', title='Dashboard')


@app.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_weightrooms():
    all_turns = SchedulesWeightRoom.query \
        .join(WeightRooms, SchedulesWeightRoom.weightroom_id == WeightRooms.id) \
        .add_columns(WeightRooms) \
        .filter(SchedulesWeightRoom.day >= datetime(datetime.today().year, datetime.today().month,
                                                    datetime.today().day))

    reservations_cnt = Reservations.query.with_entities(WeightRooms, SchedulesWeightRoom,
                                                        func.count(Reservations.schedule_weightroom_id).label('count'))\
        .join(SchedulesWeightRoom, Reservations.schedule_weightroom_id == SchedulesWeightRoom.id) \
        .join(WeightRooms, SchedulesWeightRoom.weightroom_id == WeightRooms.id) \
        .group_by(WeightRooms.id, SchedulesWeightRoom.id).all()

    class F(ReservationForm):
        pass

    for turn, weightroom in all_turns.all():
        setattr(F, str(turn.id), BooleanField())

    form = F()

    if form.validate_on_submit():
        for turn, weightroom in all_turns.all():
            if getattr(form, str(turn.id)).data:
                for res, sch in Reservations.query \
                        .join(SchedulesCourse, Reservations.schedule_course_id == SchedulesCourse.id) \
                        .add_columns(SchedulesCourse).filter(Reservations.user_id == current_user.social_number).all():

                    if sch.day == turn.day and sch.from_hour == turn.from_hour and sch.to_hour == turn.to_hour:
                        flash('Some reservations were in conflict with your courses reservations'
                              'so they were not saved', 'danger')
                        return redirect(url_for('calendar_weightrooms'))

                reservation = Reservations(user_id=current_user.social_number, schedule_weightroom_id=turn.id,
                                           schedule_course_id=None)
                db.session.add(reservation)
        db.session.commit()
        flash('All reservations were successfully saved', 'success')
        return redirect(url_for('calendar_reservations'))

    return render_template('calendars/calendar_weightrooms.html', title='Gym', all_turns=all_turns.all(),
                           schedules=all_turns.with_entities(SchedulesWeightRoom)
                           .distinct(SchedulesWeightRoom.day).all(),
                           turns=all_turns.with_entities(SchedulesWeightRoom)
                           .distinct(SchedulesWeightRoom.from_hour, SchedulesWeightRoom.to_hour).all(),
                           reservations_cnt=reservations_cnt, form=form, getattr=getattr, str=str)


@app.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    all_turns = SchedulesCourse.query \
        .join(Courses, SchedulesCourse.course_id == Courses.id) \
        .add_columns(Courses) \
        .filter(SchedulesCourse.day >= datetime(datetime.today().year, datetime.today().month,
                                                datetime.today().day))

    reservations_cnt = Reservations.query.with_entities(Courses, SchedulesCourse,
                                                        func.count(Reservations.schedule_course_id).label('count')) \
        .join(SchedulesCourse, Reservations.schedule_course_id == SchedulesCourse.id) \
        .join(Courses, SchedulesCourse.course_id == Courses.id) \
        .group_by(Courses.id, SchedulesCourse.id).all()

    class F(ReservationForm):
        pass

    for turn, course in all_turns.all():
        setattr(F, str(turn.id), BooleanField())

    form = F()

    if form.validate_on_submit():
        for turn, course in all_turns.all():
            if getattr(form, str(turn.id)).data:
                for reservation, schedule in Reservations.query \
                        .join(SchedulesWeightRoom, Reservations.schedule_weightroom_id == SchedulesWeightRoom.id) \
                        .add_columns(SchedulesWeightRoom) \
                        .filter(Reservations.user_id == current_user.social_number).all():

                    if schedule.day == turn.day and schedule.from_hour == turn.from_hour \
                            and schedule.to_hour == turn.to_hour:
                        flash('Some reservations were in conflict with your weightroom reservations '
                              ' so they were not saved', 'danger')
                        return redirect(url_for('calendar_courses'))

                reservation = Reservations(user_id=current_user.social_number, schedule_weightroom_id=None,
                                           schedule_course_id=turn.id)
                db.session.add(reservation)
        db.session.commit()
        flash('All reservations were successfully saved', 'success')
        return redirect(url_for('calendar_reservations'))

    return render_template('calendars/calendar_courses.html', title='Courses', all_turns=all_turns.all(), form=form,
                           schedules=all_turns.with_entities(SchedulesCourse)
                           .distinct(SchedulesCourse.day).all(), reservations_cnt=reservations_cnt, getattr=getattr,
                           turns=all_turns.with_entities(SchedulesCourse)
                           .distinct(SchedulesCourse.from_hour, SchedulesCourse.to_hour).all(), str=str)


@app.route('/calendar/reservations', methods=['GET', 'POST'])
@login_required
@requires_roles('member')
def calendar_reservations():
    res_courses = Reservations.query\
        .join(SchedulesCourse, Reservations.schedule_course_id == SchedulesCourse.id)\
        .join(Courses, SchedulesCourse.course_id == Courses.id)\
        .add_columns(SchedulesCourse, Courses)\
        .filter(Reservations.user_id == current_user.social_number).all()

    res_weightrooms = Reservations.query\
        .join(SchedulesWeightRoom, Reservations.schedule_weightroom_id == SchedulesWeightRoom.id) \
        .add_columns(SchedulesWeightRoom)\
        .filter(Reservations.user_id == current_user.social_number).all()

    turns = []
    days = []

    class F(CancelReservationForm):
        pass

    for reservation, schedule, course in res_courses:
        if (schedule.from_hour, schedule.to_hour) not in turns:
            turns.append((schedule.from_hour, schedule.to_hour))
        if schedule.day not in days:
            days.append(schedule.day)
        setattr(F, str(schedule.id), BooleanField())

    for reservation, schedule in res_weightrooms:
        if (schedule.from_hour, schedule.to_hour) not in turns:
            turns.append((schedule.from_hour, schedule.to_hour))
        if schedule.day not in days:
            days.append(schedule.day)
        setattr(F, str(schedule.id), BooleanField())

    form = F()

    if form.validate_on_submit():
        for reservation, schedule, course in res_courses:
            if getattr(form, str(schedule.id)).data:
                db.session.delete(Reservations.query.filter(Reservations.user_id == current_user.social_number,
                                                            Reservations.schedule_course_id == schedule.id).first())
        for reservation, schedule in res_weightrooms:
            if getattr(form, str(schedule.id)).data:
                db.session.delete(Reservations.query.filter(Reservations.user_id == current_user.social_number,
                                                            Reservations.schedule_weightroom_id == schedule.id).first())
        db.session.commit()
        flash('All reservations were successfully deleted', 'success')
        return redirect(url_for('calendar_reservations'))
    return render_template('calendars/calendar_reservations.html', title='Reservations', days=sorted(days),
                           turns=sorted(turns), res_courses=res_courses, res_weightrooms=res_weightrooms, form=form,
                           str=str, getattr=getattr)


@app.route('/calendar/instructor', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def calendar_instructor():
    schedules = Courses.query.select_from(Courses)\
        .join(SchedulesCourse, Courses.id == SchedulesCourse.course_id)\
        .add_columns(SchedulesCourse)\
        .filter(Courses.instructor_id == current_user.social_number)

    class Form(FlaskForm):
        submit = SubmitField('Delete')

    for course, schedule in schedules:
        setattr(Form, str(schedule.id), BooleanField())

    form = Form()

    if form.validate_on_submit():
        for course, schedule in schedules:
            if getattr(form, str(schedule.id)).data:
                db.session.delete(SchedulesCourse.query.filter_by(day=schedule.day, from_hour=schedule.from_hour,
                                                                  to_hour=schedule.to_hour).first())
        db.session.commit()
        flash('All schedules were successfully deleted', 'success')
        return redirect(url_for('calendar_instructor'))

    return render_template('calendars/calendar_instructor.html', title='Instructor',
                           turns=schedules.with_entities(SchedulesCourse).distinct(SchedulesCourse.from_hour).all(),
                           schedules=schedules.with_entities(SchedulesCourse)
                           .distinct(SchedulesCourse.day).limit(7).all(),
                           all_turns=schedules.all(), form=form, str=str, getattr=getattr)


@app.route('/course/create', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def course_create():
    form = CreateCourse()
    if form.validate_on_submit():
        exists = Courses.query.filter_by(name=form.name.data).first()
        if exists:
            flash(f'{form.name.data} already exists', 'danger')
        else:
            course = Courses(name=form.name.data, max_members=form.max_members.data)
            current_user.courses.append(course)
            db.session.add(course)
            db.session.commit()
            flash(f'Course {form.name.data} created successfully', 'success')
            return redirect(url_for('dashboard'))
    return render_template('admin/create_course.html', form=form)


@app.route('/course/add-event', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def course_add_event():
    form = AddEventCourse()
    if form.validate_on_submit():
        course = Courses.query.filter_by(name=form.name.data).first()
        start = str(form.turn_start.data).split(":")
        end = str(form.turn_end.data).split(":")
        if start[1] != "00" or end[1] != "00" or int(end[0]) - int(start[0]) != 1:
            flash('Turns have to be exactly 1 hour long and have to start and end at minute 00', 'danger')
        else:
            if course:
                exists = SchedulesCourse.query.filter(SchedulesCourse.from_hour == form.turn_start.data,
                                                      SchedulesCourse.to_hour == form.turn_end.data,
                                                      SchedulesCourse.course_id != course.id,
                                                      SchedulesCourse.day == form.date.data).first()
                if exists:
                    flash(f'The selected Schedule is already occupied', 'danger')
                else:
                    schedule = SchedulesCourse.query.filter(SchedulesCourse.from_hour == form.turn_start.data,
                                                            SchedulesCourse.to_hour == form.turn_end.data,
                                                            SchedulesCourse.course_id == course.id,
                                                            SchedulesCourse.day == form.date.data).first()
                    if not schedule:
                        schedule = SchedulesCourse(from_hour=form.turn_start.data, to_hour=form.turn_end.data,
                                                   course_id=course.id, day=form.date.data)
                        db.session.add(schedule)
                        db.session.commit()
                    flash(f'Successfully added an event to {form.name.data} class', 'success')
                    return redirect(url_for('calendar_courses'))
            else:
                flash(f'{form.name.data} does not exist', 'danger')
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
        flash(f'Weightroom created successfully', 'success')
        return redirect(url_for('dashboard'))
    return render_template('admin/create_weightroom.html', form=form)


@app.route('/weightroom/add-event', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def weightroom_add_event():
    form = AddEventGym()
    if form.validate_on_submit():
        weightroom = WeightRooms.query.first()
        start = str(form.turn_start.data).split(":")
        end = str(form.turn_end.data).split(":")
        if start[1] != "00" or end[1] != "00" or int(end[0]) - int(start[0]) != 1:
            flash('Turns have to be exactly 1 hour long and have to start and end at minute 00', 'danger')
        else:
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
            flash(f'Successfully added an event to the weightroom', 'success')
            return redirect(url_for('calendar_weightrooms'))
    return render_template('admin/add_event_weightroom.html', form=form)
