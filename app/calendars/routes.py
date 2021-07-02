from datetime import datetime, timedelta

from flask import Blueprint, redirect, flash, url_for, render_template
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import BooleanField, SubmitField

from app import db
from app.calendars.forms import CalendarForm
from app.models import SchedulesWeightRoom, WeightRooms, Reservations, SchedulesCourse, requires_roles, Courses

calendars = Blueprint('calendars', __name__)


@calendars.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_weightrooms():
    all_turns = SchedulesWeightRoom.query \
        .join(WeightRooms, SchedulesWeightRoom.weightroom_id == WeightRooms.id) \
        .add_columns(WeightRooms) \
        .filter(SchedulesWeightRoom.day >= datetime(datetime.today().year, datetime.today().month,
                                                    datetime.today().day),
                SchedulesWeightRoom.day <= datetime(datetime.today().year, datetime.today().month,
                                                    datetime.today().day) + timedelta(days=7))

    reservations_cnt = Reservations.query.with_entities(WeightRooms, SchedulesWeightRoom,
                                                        func.count(Reservations.schedule_weightroom_id).label('count')) \
        .join(SchedulesWeightRoom, Reservations.schedule_weightroom_id == SchedulesWeightRoom.id) \
        .join(WeightRooms, SchedulesWeightRoom.weightroom_id == WeightRooms.id) \
        .group_by(WeightRooms.id, SchedulesWeightRoom.id).all()

    if current_user.role == 'instructor':
        submit_str = 'Delete'
    if current_user.role == 'member':
        submit_str = 'Reserve Now'

    class F(FlaskForm):
        submit = SubmitField(submit_str)

    for turn, weightroom in all_turns.all():
        setattr(F, str(turn.id), BooleanField())

    form = F()

    if form.validate_on_submit():
        for turn, weightroom in all_turns.all():
            if getattr(form, str(turn.id)).data:
                if current_user.role == 'member':
                    for res, sch in Reservations.query \
                            .join(SchedulesCourse, Reservations.schedule_course_id == SchedulesCourse.id) \
                            .add_columns(SchedulesCourse).filter(Reservations.user_id == current_user.social_number).all():

                        if sch.day == turn.day and sch.from_hour == turn.from_hour and sch.to_hour == turn.to_hour:
                            flash('Some reservations were in conflict with your courses reservations' +
                                  ' so they were not saved', 'danger')
                            return redirect(url_for('calendar_weightrooms'))

                    reservation = Reservations(user_id=current_user.social_number, schedule_weightroom_id=turn.id,
                                               schedule_course_id=None)
                    db.session.add(reservation)
                if current_user.role == 'instructor':
                    db.session.delete(SchedulesWeightRoom.query.filter_by(day=turn.day, from_hour=turn.from_hour,
                                                                          to_hour=turn.to_hour).first())
        db.session.commit()
        if current_user.role == 'member':
            flash('All reservations were successfully saved', 'success')
            return redirect(url_for('calendar_reservations'))
        if current_user.role == 'instructor':
            flash('All schedules were successfully deleted', 'success')
            return redirect(url_for('calendar_weightrooms'))

    return render_template('calendars/calendar_weightrooms.html', title='Gym', all_turns=all_turns.all(),
                           schedules=all_turns.with_entities(SchedulesWeightRoom)
                           .distinct(SchedulesWeightRoom.day).limit(7).all(),
                           turns=all_turns.with_entities(SchedulesWeightRoom)
                           .distinct(SchedulesWeightRoom.from_hour, SchedulesWeightRoom.to_hour).all(),
                           reservations_cnt=reservations_cnt, form=form, getattr=getattr, str=str)


@calendars.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    all_turns = SchedulesCourse.query \
        .join(Courses, SchedulesCourse.course_id == Courses.id) \
        .add_columns(Courses) \
        .filter(SchedulesCourse.day >= datetime(datetime.today().year, datetime.today().month,
                                                datetime.today().day),
                SchedulesCourse.day <= datetime(datetime.today().year, datetime.today().month,
                                                datetime.today().day) + timedelta(days=7))

    reservations_cnt = Reservations.query.with_entities(Courses, SchedulesCourse,
                                                        func.count(Reservations.schedule_course_id).label('count')) \
        .join(SchedulesCourse, Reservations.schedule_course_id == SchedulesCourse.id) \
        .join(Courses, SchedulesCourse.course_id == Courses.id) \
        .group_by(Courses.id, SchedulesCourse.id).all()

    class Form(CalendarForm):
        pass

    for turn, course in all_turns.all():
        setattr(Form, str(turn.id), BooleanField())

    form = Form()

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
                        return redirect(url_for('calendars.calendar_courses'))

                reservation = Reservations(user_id=current_user.social_number, schedule_weightroom_id=None,
                                           schedule_course_id=turn.id)
                db.session.add(reservation)
        db.session.commit()
        flash('All reservations were successfully saved', 'success')
        return redirect(url_for('calendars.calendar_reservations'))

    return render_template('calendars/calendar_courses.html', title='Courses', all_turns=all_turns.all(), form=form,
                           schedules=all_turns.with_entities(SchedulesCourse)
                           .distinct(SchedulesCourse.day).limit(7).all(), reservations_cnt=reservations_cnt,
                           turns=all_turns.with_entities(SchedulesCourse)
                           .distinct(SchedulesCourse.from_hour, SchedulesCourse.to_hour).all(), str=str,
                           getattr=getattr)


@calendars.route('/calendar/reservations', methods=['GET', 'POST'])
@login_required
@requires_roles('member')
def calendar_reservations():
    res_courses = Reservations.query \
        .join(SchedulesCourse, Reservations.schedule_course_id == SchedulesCourse.id) \
        .join(Courses, SchedulesCourse.course_id == Courses.id) \
        .add_columns(SchedulesCourse, Courses) \
        .filter(Reservations.user_id == current_user.social_number,
                SchedulesCourse.day >= datetime(datetime.today().year, datetime.today().month,
                                                datetime.today().day),
                SchedulesCourse.day <= datetime(datetime.today().year, datetime.today().month,
                                                datetime.today().day) + timedelta(days=7)).all()

    res_weightrooms = Reservations.query \
        .join(SchedulesWeightRoom, Reservations.schedule_weightroom_id == SchedulesWeightRoom.id) \
        .add_columns(SchedulesWeightRoom) \
        .filter(Reservations.user_id == current_user.social_number,
                SchedulesWeightRoom.day >= datetime(datetime.today().year, datetime.today().month,
                                                    datetime.today().day),
                SchedulesWeightRoom.day <= datetime(datetime.today().year, datetime.today().month,
                                                    datetime.today().day) + timedelta(days=7)).all()

    turns = []
    days = []

    class Form(CalendarForm):
        pass

    for reservation, schedule, course in res_courses:
        if (schedule.from_hour, schedule.to_hour) not in turns:
            turns.append((schedule.from_hour, schedule.to_hour))
        if schedule.day not in days:
            days.append(schedule.day)
        setattr(Form, str(schedule.id), BooleanField())

    for reservation, schedule in res_weightrooms:
        if (schedule.from_hour, schedule.to_hour) not in turns:
            turns.append((schedule.from_hour, schedule.to_hour))
        if schedule.day not in days:
            days.append(schedule.day)
        setattr(Form, str(schedule.id), BooleanField())

    form = Form()

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
        return redirect(url_for('calendars.calendar_reservations'))
    return render_template('calendars/calendar_reservations.html', title='Reservations', days=sorted(days),
                           turns=sorted(turns), res_courses=res_courses, res_weightrooms=res_weightrooms, form=form,
                           str=str, getattr=getattr)


@calendars.route('/calendar/instructor', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def calendar_instructor():
    schedules = Courses.query.select_from(Courses) \
        .join(SchedulesCourse, Courses.id == SchedulesCourse.course_id) \
        .add_columns(SchedulesCourse) \
        .filter(Courses.instructor_id == current_user.social_number)

    class Form(CalendarForm):
        pass

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
        return redirect(url_for('calendars.calendar_instructor'))

    return render_template('calendars/calendar_instructor.html', title='Instructor', str=str, getattr=getattr,
                           turns=schedules.with_entities(SchedulesCourse).distinct(SchedulesCourse.from_hour).all(),
                           schedules=schedules.with_entities(SchedulesCourse)
                           .distinct(SchedulesCourse.day).limit(7).all(), all_turns=schedules.all(), form=form)
