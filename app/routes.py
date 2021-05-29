from flask import render_template, url_for, flash, redirect
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditProfileForm, ReservationForm, CreateCourse, AddEventCourse, \
    AddEventGym, CreateWeightRoom
from app.models import User, Course, Schedule, requires_roles, WeightRoom, ScheduleCourse, ScheduleWeightRoom
from flask_login import login_user, current_user, logout_user, login_required
from wtforms import BooleanField


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


@app.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_gym():
    turns = ScheduleWeightRoom.query.distinct(ScheduleWeightRoom.from_hour, ScheduleWeightRoom.to_hour).all()
    schedules = Schedule.query.join(Schedule.weightrooms).filter_by(id=ScheduleWeightRoom.schedule_id).all()

    class F(ReservationForm):
        pass

    form = F()

    for turn in turns:
        for schedule in schedules:
            setattr(F, str(turn.from_hour.strftime('%H')) + str(schedule.day.strftime('%A')),
                    BooleanField('Reserve Now'))

    if form.validate_on_submit():
        for turn in turns:
            for schedule in schedules:
                if getattr(form, str(turn.from_hour) + str(schedule.day)).data:
                    pass  # TODO if checked

    return render_template('calendar_gym.html', title='Gym Calendar',
                           schedules=schedules, turns=turns, form=form, getattr=getattr, str=str)


@app.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    form = ReservationForm()
    turns = ScheduleCourse.query.distinct(ScheduleCourse.from_hour, ScheduleCourse.to_hour).all()
    allturns = ScheduleCourse.query.all()
    schedules = Schedule.query.join(Schedule.courses).filter_by(id=ScheduleCourse.schedule_id).all()
    courses = Course.query.all()
    return render_template('calendar_courses.html', title='Course Calendar', schedules=schedules, turns=turns,
                           allturns=allturns, courses=courses, form=form, str=str, getattr=getattr)


@app.route('/calendar/instructor')
@login_required
@requires_roles('instructor')
def calendar_instructor():
    turns = ScheduleCourse.query.all()
    schedules = Schedule.query.limit(7).all()
    courses = Course.query.filter_by(instructor_id=current_user.get_id())
    return render_template('admin/calendar_instructor.html', title='Instructor Calendar', turns=turns,
                           schedules=schedules, courses=courses)


@app.route('/course/create', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def create_course():
    form = CreateCourse()
    if form.validate_on_submit():
        course = Course(name=form.name.data, max_members=form.max_members.data)
        current_user.courses.append(course)
        db.session.add(course)
        db.session.commit()
        # flash(f'Course {form.name.data} created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('admin/create_course.html', form=form)


@app.route('/course/add-event', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def add_event_course():
    form = AddEventCourse()
    if form.validate_on_submit():
        course = Course.query.filter_by(name=form.name.data).first()
        schedule = Schedule.query.filter_by(day=form.date.data).first()
        if not schedule:
            schedule = Schedule(day=form.date.data)
            db.session.add(schedule)
        turn = ScheduleCourse.query.filter(ScheduleCourse.from_hour == form.turn_start.data,
                                           ScheduleCourse.to_hour == form.turn_end.data,
                                           ScheduleCourse.course_id == course.id,
                                           ScheduleCourse.schedule_id == schedule.id).first()
        # print(turn.from_hour, turn.to_hour, turn.course_id, course.id, turn.schedule_id, schedule.id, schedule.day, course.name)
        if not turn:
            turn = ScheduleCourse(from_hour=form.turn_start.data, to_hour=form.turn_end.data, course_id=course.id,
                                  schedule_id=schedule.id)
            db.session.add(turn)
        """
        if turn not in schedule.turns:
            schedule.turns.append(turn)
        if schedule not in course.schedules:
            course.schedules.append(schedule)
        """
        db.session.commit()
        # flash(f'Successfully added an event to {form.name.data} class', 'success')
        return redirect(url_for('calendar_courses'))
    return render_template('admin/add_event.html', form=form)


@app.route('/weightroom/create', methods=['GET', 'POST'])
def create_weightroom():
    weightroom = WeightRoom.query.first()
    form = CreateWeightRoom(obj=weightroom)
    if form.validate_on_submit():
        if not weightroom:
            weightroom = WeightRoom(max_members=form.max_members.data, dimension=form.dimension.data)
            db.session.add(weightroom)
        else:
            weightroom.max_members = form.max_members.data
            weightroom.dimension = form.dimension.data
        db.session.commit()
        # flash(f'Course {form.name.data} created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('admin/create_weightroom.html', form=form)


@app.route('/weightroom/add-event', methods=['GET', 'POST'])
def add_event_gym():
    form = AddEventGym()
    if form.validate_on_submit():
        weightroom = WeightRoom.query.first()
        if not weightroom:
            return redirect(url_for('admin/create_weightroom'))
        schedule = Schedule.query.filter_by(day=form.date.data).first()
        if not schedule:
            schedule = Schedule(day=form.date.data)
            db.session.add(schedule)
        turn = ScheduleWeightRoom.query.filter(ScheduleWeightRoom.from_hour == form.turn_start.data,
                                               ScheduleWeightRoom.to_hour == form.turn_end.data,
                                               ScheduleWeightRoom.weightroom_id == weightroom.id,
                                               ScheduleWeightRoom.schedule_id == schedule.id).first()
        if not turn:
            turn = ScheduleWeightRoom(from_hour=form.turn_start.data, to_hour=form.turn_end.data,
                                      weightroom_id=weightroom.id, schedule_id=schedule.id)
            db.session.add(turn)
        """
        if turn not in schedule.turns:
            schedule.turns.append(turn)
        if schedule not in weightroom.schedules:
            weightroom.schedules.append(schedule)
        """
        db.session.commit()
        # flash(f'Successfully added an event to {form.name.data} class', 'success')
        return redirect(url_for('calendar_gym'))
    return render_template('admin/add_event_weightroom.html', form=form)
