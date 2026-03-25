from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class PipelineJob(db.Model):
    __tablename__ = 'pipeline_jobs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    jenkins_url = db.Column(db.String(300), nullable=False)
    
    builds = db.relationship('PipelineBuild', backref='job', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<PipelineJob {self.name}>'

class PipelineBuild(db.Model):
    __tablename__ = 'pipeline_builds'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('pipeline_jobs.id'), nullable=False)
    build_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False) # SUCCESS, FAILURE, ABORTED
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration_ms = db.Column(db.Integer, default=0)
    
    # Optional: store truncated logs or specific error messages
    log_snippet = db.Column(db.Text, nullable=True)
    
    # Classification results
    failure_type = db.Column(db.String(100), default='None')
    failure_details = db.Column(db.Text, nullable=True)
    root_cause_title = db.Column(db.String(250), nullable=True)
    explanation = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('job_id', 'build_number', name='_job_build_uc'),
    )

    def __repr__(self):
        return f'<PipelineBuild {self.job.name} #{self.build_number} - {self.status}>'
