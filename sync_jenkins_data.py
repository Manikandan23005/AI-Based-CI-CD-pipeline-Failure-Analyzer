from app import app
from database import db, PipelineJob, PipelineBuild
from jenkins_client import jenkins_client
from analyzer import analyzer
from datetime import datetime
import json
import logging

def sync_data():
    with app.app_context():
        # Ensure DB tables exist but do NOT drop them for incremental syncing
        db.create_all()

        try:
            jobs = jenkins_client.get_all_jobs()
        except Exception as e:
            print(f"Background Poller: Error authenticating or connecting to Jenkins: {e}")
            return

        for j in jobs:
            job_name = j.get('name')
            job_url = j.get('url')

            job = PipelineJob.query.filter_by(name=job_name).first()
            if not job:
                job = PipelineJob(name=job_name, jenkins_url=job_url)
                db.session.add(job)
                db.session.commit()

            try:
                job_info = jenkins_client.get_job_info(job_name)
                builds = job_info.get('builds', [])

                for b in builds:
                    build_number = b['number']
                    
                    # Check if build is already parsed in our DB skip if true, UNLESS it's a legacy error that needs LLM re-parsing
                    existing_build = PipelineBuild.query.filter_by(job_id=job.id, build_number=build_number).first()
                    is_update = False
                    
                    if existing_build:
                        if existing_build.failure_type in ['Unknown Error', 'API Key Missing', 'Unmapped Error', 'LLM Fallback', 'Dynamic Analysis Extraction', 'Extracted Context']:
                            is_update = True
                        else:
                            continue

                    try:
                        b_info = jenkins_client.get_build_info(job_name, build_number)
                        
                        if b_info.get('building', True):
                            continue
                            
                        status = b_info.get('result', 'UNKNOWN')
                        timestamp_ms = b_info.get('timestamp', 0)
                        duration_ms = b_info.get('duration', 0)
                        dt = datetime.utcfromtimestamp(timestamp_ms / 1000.0)
                        
                        try:
                            console_log = jenkins_client.get_build_console_log(job_name, build_number)
                        except Exception:
                            console_log = ""

                        if status == 'SUCCESS' or status == 'ABORTED':
                            snippet = "Build passed or aborted smoothly."
                            analysis = {
                                'failure_type': 'None',
                                'root_cause_title': 'Success',
                                'explanation': 'The pipeline essentially completed its tasks successfully.',
                                'snippet': snippet
                            }
                        else:
                            try:
                                job_config = jenkins_client.get_job_config(job_name)
                            except Exception:
                                job_config = ""
                            analysis = analyzer.analyze(console_log, job_config)

                        if is_update:
                            existing_build.status = status
                            existing_build.timestamp = dt
                            existing_build.duration_ms = duration_ms
                            existing_build.log_snippet = analysis['snippet']
                            existing_build.failure_type = analysis['failure_type']
                            existing_build.failure_details = analysis['snippet']
                            existing_build.root_cause_title = analysis['root_cause_title']
                            existing_build.explanation = analysis.get('explanation')
                            db.session.commit()
                            print(f"Live Sync API Updated Build: #{build_number} ({status}) | Analyzed: {analysis['failure_type']}")
                        else:
                            build = PipelineBuild(
                                job_id=job.id,
                                build_number=build_number,
                                status=status,
                                timestamp=dt,
                                duration_ms=duration_ms,
                                log_snippet=analysis['snippet'],
                                failure_type=analysis['failure_type'],
                                failure_details=analysis['snippet'],
                                root_cause_title=analysis['root_cause_title'],
                                explanation=analysis.get('explanation')
                            )
                            db.session.add(build)
                            db.session.commit()
                            print(f"Live Sync API Detected [NEW] Build: #{build_number} ({status}) | Analyzed: {analysis['failure_type']}")

                    except Exception as e:
                        print(f"Background Sync Failed fetching build #{build_number}: {e}")

            except Exception:
                pass
        
        db.session.commit()

if __name__ == '__main__':
    sync_data()
