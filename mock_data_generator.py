from app import app
from database import db, PipelineJob, PipelineBuild
from analyzer import analyzer
import random
from datetime import datetime, timedelta

def generate_mock_data():
    with app.app_context():
        db.create_all()


        if PipelineJob.query.count() == 0:
            frontend_job = PipelineJob(name="Frontend-UI-Deploy", jenkins_url="http://localhost:8080/job/Frontend-UI-Deploy")
            backend_job = PipelineJob(name="Backend-API-Deploy", jenkins_url="http://localhost:8080/job/Backend-API-Deploy")
            db.session.add(frontend_job)
            db.session.add(backend_job)
            db.session.commit()


        PipelineBuild.query.delete()
        db.session.commit()

        jobs = PipelineJob.query.all()
        now = datetime.utcnow()

        mock_logs = {
            'Dependency Error': "Installing dependencies...\nERROR: Could not resolve dependencies for com.example:backend:1.0.0\nFailed to read artifact descriptor",
            'Environment Issue': "Started by user Satoru\nBuilding in workspace /var/lib/jenkins/workspace/proj\nCannot connect to Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?",
            'Test Failure': "Running Test Suite...\nExpected condition not matched\nTests run: 154, Failures: 3, Errors: 0, Skipped: 1",
            'Build Failure': "Compiling 45 source files...\n[ERROR] COMPILATION ERROR : \n/src/main/App.java:[45,15] error: cannot find symbol",
            'Unknown Error': "Task completed.\nProcess exited with status 137\nSegmentation fault",
            'None': "Building in workspace...\nAll tasks completed successfully.\nSUCCESS"
        }

        build_counter = 100
        for job in jobs:
            for i in range(50):
                build_counter += 1
                status = random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILURE", "FAILURE", "ABORTED"])
                timestamp = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))

                if status == 'SUCCESS' or status == 'ABORTED':
                    failure_type = 'None'
                    snippet = mock_logs['None'] if status == 'SUCCESS' else 'Build aborted by user.'
                else:
                    failure_type = random.choice([k for k in mock_logs.keys() if k != 'None'])
                    snippet = mock_logs[failure_type]


                analyzed_type, final_snippet = analyzer.analyze(snippet)

                build = PipelineBuild(
                    job_id=job.id,
                    build_number=build_counter,
                    status=status,
                    timestamp=timestamp,
                    duration_ms=random.randint(10000, 300000),
                    log_snippet=snippet,
                    failure_type=analyzed_type if status == 'FAILURE' else 'None',
                    failure_details=final_snippet if status == 'FAILURE' else None
                )
                db.session.add(build)

        db.session.commit()
        print("Mock data generated successfully!")

if __name__ == '__main__':
    generate_mock_data()
