from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.admin.forms import CreateWeightRoom, AddEventGym, CreateCourse, AddEventCourse
from app.models import requires_roles, WeightRooms, SchedulesWeightRoom, Courses, SchedulesCourse

admin = Blueprint('admin', __name__)


@admin.route('/dashboard')
@login_required
@requires_roles('instructor')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@admin.route('/weightroom/create', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_weightroom.html', form=form)


@admin.route('/weightroom/add-event', methods=['GET', 'POST'])
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
            if weightroom:
                schedule = SchedulesWeightRoom.query.filter(SchedulesWeightRoom.from_hour == form.turn_start.data,
                                                            SchedulesWeightRoom.to_hour == form.turn_end.data,
                                                            SchedulesWeightRoom.weightroom_id == weightroom.id,
                                                            SchedulesWeightRoom.day == form.date.data).first()
                if schedule:
                    flash(f'That schedule already exists', 'danger')
                else:
                    db.session.add(SchedulesWeightRoom(from_hour=form.turn_start.data, to_hour=form.turn_end.data,
                                                       weightroom_id=weightroom.id, day=form.date.data))
                    db.session.commit()
                    flash(f'Successfully added an event to the weightroom', 'success')
                    return redirect(url_for('calendars.calendar_weightrooms'))

    return render_template('admin/add_event_weightroom.html', form=form)


@admin.route('/course/create', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def course_create():
    form = CreateCourse()
    if form.validate_on_submit():
        course = Courses(name=form.name.data, max_members=form.max_members.data)
        current_user.courses.append(course)
        db.session.add(course)
        db.session.commit()
        flash(f'Course {form.name.data} created successfully', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_course.html', form=form)


@admin.route('/course/add-event', methods=['GET', 'POST'])
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
            schedule = SchedulesCourse.query.filter(SchedulesCourse.from_hour == form.turn_start.data,
                                                    SchedulesCourse.to_hour == form.turn_end.data,
                                                    SchedulesCourse.day == form.date.data).first()
            if schedule:
                flash(f'That schedule already exists', 'danger')
            else:
                db.session.add(SchedulesCourse(from_hour=form.turn_start.data, to_hour=form.turn_end.data,
                                               course_id=course.id, day=form.date.data))
                db.session.commit()
                flash(f'Successfully added an event to {form.name.data} class', 'success')
                return redirect(url_for('calendars.calendar_courses'))

    return render_template('admin/add_event.html', form=form)


@admin.route('/course/delete', methods=['GET', 'POST'])
@login_required
@requires_roles('instructor')
def delete_course():
    return render_template('admin/delete_course.html')
