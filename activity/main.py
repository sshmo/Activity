from sqlalchemy import func
from datetime import datetime, timedelta
from .models import Activity, Scores
from . import db
from .apology import apology
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, render_template, request, flash, url_for
import pandas as pd
import calplot
from matplotlib import rcParams
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Times New Roman']

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():

    user_id = current_user.user_id
    rows = Activity.query.filter_by(user_id=user_id).all()

    activities = {}
    activities['logged_in'] = current_user.__bool__

    # Table data structure definition
    data = {'#': [],
            'Activity': [],
            'Target': [],
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            'Percent': [],
            'Grade': [],
            'Priority': [],
            }

    # sum row initialization
    data['#'].append(0)
    data['Activity'].append('Total')
    data['Target'].append(0)
    data[0].append(0)
    data[1].append(0)
    data[2].append(0)
    data[3].append(0)
    data[4].append(0)
    data[5].append(0)
    data[6].append(0)
    data['Percent'].append(0)
    data['Grade'].append(0)
    data['Priority'].append(0)

    n = 0  # number of rows inserted in data
    for row in rows:
        # Query database for scores
        n += 1
        data['#'].append(n)
        data["Activity"].append(row.act_name)
        data["Target"].append(row.act_score)

        # query for the scores in the past week
        since = datetime.utcnow().date() - timedelta(days=6)

        score_rows = Scores.query.filter((Scores.act_id == row.act_id) &
                                         (Scores.user_id == user_id) &
                                         (Scores.score_time >= since)
                                         ).all()

        # percent, grade and priority initialization for each activity
        data["Percent"].append(0)
        data["Grade"].append(0)
        data["Priority"].append(0)

        # fill scores for each activity with a record in the score table
        for score_row in score_rows:

            score_value = score_row.score_value
            score_time = score_row.score_time
            score_day = score_time.weekday()

            data[score_day].append(score_value)
            data[score_day][0] += score_value
            data["Percent"][n] += score_value / 7 / row.act_score * 100

        # the score for that day was not available from score table, so it was unscored(was zero)
        for i in range(0, 7):
            if len(data[i]) < n + 1:
                data[i].append(0)

        # calculating geade score (= (today score + average score)/2)
        today = datetime.utcnow().weekday()  # today = datetime.today().weekday()

        percent_score = data["Percent"][n]
        today_score = data[today][n]

        data["Grade"][n] = (today_score + percent_score*row.act_score/100)/2
        grade_score = data["Grade"][n]

        # calculating priority
        data["Priority"][n] = 10 - (row.act_score - grade_score) + 1
        data['Target'][0] += row.act_score

    df = pd.DataFrame(data)

    df_sum = df.loc[0]
    df_data = df.loc[1:]
    df_sorted = df_data.sort_values(by=['Priority'], ignore_index=True)

    df_prio = df_sorted.append(df_sum, ignore_index=True)

    df_prio["Percent"] = df_prio["Percent"].round(1)
    df_prio["Grade"] = df_prio["Grade"].round(1)
    df_prio["Priority"] = df_prio["Priority"].round(0)
    df_prio["Priority"] = df_prio["Priority"].astype("int")

    df_prio.replace(0, '-', inplace=True)

    sum_index = df_prio.shape[0] - 1
    activities['df_prio'] = df_prio
    activities['sum_index'] = sum_index

    return render_template("index.html", activities=activities)


@main.route('/heatmap', methods=["GET", "POST"])
@login_required
def heatmap():

    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":

        user_id = current_user.user_id
        activity = request.form.get('activity')

        if activity == 'Total':
            # query score table for user total activity in each day
            scores = Scores.query.with_entities(func.DATE(Scores.score_time),
                                                func.sum(Scores.score_value))\
                .filter_by(user_id=user_id)\
                .group_by(func.DATE(Scores.score_time))\
                .order_by(func.DATE(Scores.score_time))\
                .all()

            list_score = []
            list_index = []
            for i in range(0, len(scores)):
                list_score.append(scores[i][1])
                list_index.append(scores[i][0])
            Index = pd.to_datetime(list_index)
            events = pd.Series(list_score, index=Index)

        else:
            # query score table for user activity in each day
            scores = Scores.query.filter((Scores.user_id == user_id) & (Scores.score_name == activity))\
                .order_by(Scores.score_time).all()

            list_score = []
            list_index = []
            for i in range(0, len(scores)):
                list_score.append(scores[i].score_value)
                list_index.append(scores[i].score_time)
            Index = pd.to_datetime(list_index)
            events = pd.Series(list_score, index=Index)

        from io import BytesIO
        img = BytesIO()

        calplot.calplot(events, monthticks=1, dayticks=[
                        0, 2, 4, 6], daylabels='MTWTFSS')

        import base64
        plt.savefig(img, format='png', bbox_inches='tight',
                    transparent=True, facecolor="None")
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

        activities = [plot_url]

        # query activity table for user activities
        rows = Activity.query.filter_by(user_id=current_user.user_id).all()

        # query score table for each activity that had scored today
        for row in rows:
            activities.append(row.act_name)

        activities.append("Total")
        activities.append("POST")

        return render_template('heatmap.html', activities=activities)

    # User reached route via GET (as by clicking a link or via redirect)

    user_id = current_user.user_id

    # query activity table for user activities
    rows = Activity.query.filter_by(user_id=current_user.user_id).all()

    activities = []

    activities.append(current_user.__bool__)

    # query score table for each activity that had scored today
    for row in rows:
        activities.append(row.act_name)

    activities.append("Total")
    activities.append("GET")

    return render_template("heatmap.html", activities=activities)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', activities=current_user.__bool__)


@main.route("/add_activity", methods=["GET", "POST"])
@login_required
def add_activity():
    '''adds activity to the database'''

    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":

        user_id = current_user.user_id
        activity = request.form.get('activity')

        # Ensure activity was submitted
        if not activity:
            flash('Must provide activity.')
            return redirect(url_for('main.add_activity'))

        score = request.form.get('score')

        # Ensure activity was submitted
        if not score:
            flash('Must provide score.')
            return redirect(url_for('main.add_activity'))

        rows = Activity.query.filter_by(user_id=current_user.user_id).all()

        activities = []
        for row in rows:
            activities.append(row.act_name)

        if activity in activities:
            flash('You already added this activity')
            return redirect(url_for('main.add_activity'))

        # create new activity with the form data.
        new_act = Activity(act_name=activity,
                           act_score=score,
                           user_id=user_id)

        # add the new user to the database
        db.session.add(new_act)
        db.session.commit()

        return redirect("/")

    return render_template("add_activity.html", activities=current_user.__bool__)


@main.route("/add_score", methods=["GET", "POST"])
@login_required
def add_score():
    """adds activity score to the database"""

    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":

        user_id = current_user.user_id
        activity_name = request.form.get('activity')

        # Ensure activity was submitted
        if not activity_name:
            flash('Must provide activity.')
            return redirect(url_for('main.add_score'))

        score_value = request.form.get('score')

        # Ensure activity was submitted
        if not score_value:
            flash('Must provide score.')
            return redirect(url_for('main.add_score'))

        # Query database for activity
        activity = Activity.query.filter((Activity.act_name == activity_name) &
                                         (Activity.user_id == user_id)).all()
        act_id = activity[0].act_id
        score_value = int(score_value)

        # make new hypothetical records of activity
        # from random import randint
        # for i in range(0, 20):
        #     since = datetime.utcnow() - timedelta(days = i)
        #     # Update user scores in the scores table
        #     new_score = Scores(score_name=activity_name,
        #                    score_value= randint(1, 20),
        #                    user_id=user_id,
        #                    act_id=act_id,
        #                    score_time = since)

        #     # add the new user to the database
        #     db.session.add(new_score)
        #     db.session.commit()

        # make new record of activity
        new_score = Scores(score_name=activity_name,
                           score_value=score_value,
                           user_id=user_id,
                           act_id=act_id,)

        # add the new user to the database
        db.session.add(new_score)
        db.session.commit()

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)

    user_id = current_user.user_id

    # query activity table for user activities
    rows = Activity.query.filter_by(user_id=current_user.user_id).all()

    activities = []

    activities.append(current_user.__bool__)

    # query score table for each activity that had scored today
    for row in rows:
        score = Scores.query.filter((Scores.user_id == user_id) &
                                    (Scores.score_name == row.act_name) &
                                    (Scores.score_time >= datetime.utcnow().date())
                                    ).all()
        # show only activities that with no score today
        if not score:
            activities.append(row.act_name)

    return render_template("add_score.html", activities=activities)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    main.errorhandler(code)(errorhandler)
