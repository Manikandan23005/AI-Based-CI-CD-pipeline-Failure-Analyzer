import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from database import db, PipelineJob, PipelineBuild, User
from sqlalchemy import func
from datetime import datetime
from analyzer import analyzer
import logging

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import threading
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///analyzer.db?timeout=20'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key-123'

db.init_app(app)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/api/sync', methods=['POST'])
@login_required
def manual_sync():
    """Manually triggers background ML polling to extract missing records pulling raw scripts down asynchronously."""
    try:
        from sync_jenkins_data import sync_data
        sync_data()
        return jsonify({'status': 'success', 'message': 'Successfully synchronized ML layers with raw Jenkins boundaries.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('signup.html', error="Username already exists")
            
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('dashboard'))
        
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('landing.html')



@app.route('/')
def landing():
    """Public stunning landing page mapped explicitly to showcase functionalities."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    total_builds = PipelineBuild.query.count()
    failed_builds = PipelineBuild.query.filter_by(status='FAILURE').count()
    success_builds = PipelineBuild.query.filter_by(status='SUCCESS').count()
    
    recent_failures = PipelineBuild.query.filter_by(status='FAILURE').order_by(PipelineBuild.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                            total=total_builds, 
                            failed=failed_builds,
                            success=success_builds,
                            recent_failures=recent_failures)

@app.route('/builds')
@login_required
def builds_list():
    """Displays a list of all builds."""
    page = request.args.get('page', 1, type=int)
    pagination = PipelineBuild.query.order_by(PipelineBuild.timestamp.desc()).paginate(page=page, per_page=15)
    return render_template('builds.html', pagination=pagination)

@app.route('/build/<int:build_id>')
@login_required
def build_details(build_id):
    """Specific build details and analysis view."""
    build = PipelineBuild.query.get_or_404(build_id)
    return render_template('build_details.html', build=build)

@app.errorhandler(404)
def not_found_error(error):
    return redirect(url_for('dashboard'))

@app.route('/api/stats')
@login_required
def api_stats():
    success = PipelineBuild.query.filter_by(status='SUCCESS').count()
    failed = PipelineBuild.query.filter_by(status='FAILURE').count()
    aborted = PipelineBuild.query.filter_by(status='ABORTED').count()
    total = success + failed + aborted

    return jsonify({
        'labels': ['Successful', 'Failed', 'Aborted'],
        'data': [success, failed, aborted],
        'total': total
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
