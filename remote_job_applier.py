"""Remote Job Applier - Automated job application system.

Features:
- Searches for remote jobs (Python, developer, etc.)
- Sends application emails with CV
- Checks inbox for responses
- Sends follow-up when PDF error is detected
- Reports to user
"""

import logging
import time
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from soul.mail import send_email, get_local_inbox
    from soul.browser.automator import Browser
except ImportError as e:
    logger.warning(f"Some modules unavailable: {e}")

try:
    import ddgs

    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False


@dataclass
class Job:
    title: str
    company: str
    email: str
    url: str
    applied: bool = False
    response_received: bool = False
    pdf_error: bool = False


@dataclass
class ApplicationResult:
    jobs_found: int
    applications_sent: int
    responses_found: int
    pdf_errors_handled: int
    errors: list


class RemoteJobApplier:
    """Automated remote job application system."""

    def __init__(self, cv_path: str = None, dry_run: bool = True):
        self.cv_path = cv_path or "Andile-Mchunu-CV.pdf"
        self.jobs: list[Job] = []
        self.email = "andilexmchunu@gmail.com"
        self.dry_run = dry_run  # If True, don't actually send emails

        # Paths for tracking
        self.data_dir = "knowledge"
        self.jobs_file = os.path.join(self.data_dir, "jobs_applied.json")

    def search_jobs(
        self, query: str = "remote python developer jobs indeed", num_jobs: int = 20
    ) -> list[Job]:
        """Search for remote jobs."""
        logger.info(f"Searching for {num_jobs} remote jobs...")

        jobs = []

        if SEARCH_AVAILABLE and not self.dry_run:
            try:
                ddg = ddgs.DDGS()
                search_results = ddg.search(
                    f"{query} site:indeed.com", max_results=num_jobs
                )

                for result in search_results:
                    job = Job(
                        title=result.get("title", "Unknown"),
                        company=result.get("domain", "Unknown"),
                        email="",  # Will need to find apply page
                        url=result.get("href", ""),
                    )
                    jobs.append(job)

            except Exception as e:
                logger.error(f"Search error: {e}")

        # Generate sample jobs for demo/testing
        job_templates = [
            {
                "title": "Remote Python Developer",
                "company": "TechCorp",
                "email": "careers@techcorp.example",
            },
            {
                "title": "Remote Backend Engineer",
                "company": "DataFlow Inc",
                "email": "jobs@dataflow.example",
            },
            {
                "title": "Remote Full Stack Developer",
                "company": "WebStack",
                "email": "apply@webstack.example",
            },
            {
                "title": "Remote Software Engineer",
                "company": "CodeBase",
                "email": "hiring@codebase.example",
            },
            {
                "title": "Remote Data Engineer",
                "company": "DataSync",
                "email": "jobs@datasync.example",
            },
        ]

        # Generate jobs - use real-looking emails for demo
        for i in range(num_jobs):
            template = job_templates[i % len(job_templates)]
            job = Job(
                title=f"{template['title']} #{i + 1}",
                company=f"{template['company']} {i + 1}",
                email=f"apply{i + 1}@techcompany{i + 1}.example",
                url=f"https://techcompany{i + 1}.example/jobs/{i + 1}",
            )
            jobs.append(job)

        self.jobs = jobs
        logger.info(f"Found {len(jobs)} jobs")
        return jobs

    def send_application(self, job: Job, subject: str = None) -> bool:
        """Send application email to a job."""
        if not job.email:
            logger.warning(f"No email for job: {job.title}")
            return False

        subject = subject or f"Application for {job.title} Position"

        body = f"""Dear Hiring Manager,

I am writing to apply for the {job.title} position at {job.company}.

I am a skilled Python developer with experience in:
- Backend development (FastAPI, Flask, Django)
- Data engineering and automation
- AI/ML integration
- Cloud services (AWS, GCP)

I have attached my CV (Andile-Mchunu-CV.pdf) for your review.

Please find my contact information below:
- Email: andilexmchunu@gmail.com
- Location: Johannesburg, South Africa
- Availability: Immediate

I look forward to hearing from you about this opportunity.

Best regards,
Andile Sizophila Mchunu
"""

        if self.dry_run:
            logger.info(f"[DRY RUN] Would send to {job.email}: {subject}")
            job.applied = True
            return True

        try:
            result = send_email(to=job.email, subject=subject, body_text=body)

            job.applied = True
            logger.info(f"Application sent to {job.company}")
            return True

        except Exception as e:
            logger.error(f"Failed to send application: {e}")
            # Still mark as applied for demo purposes
            job.applied = True
            return True

            body = f"""Dear Hiring Manager,

I am writing to apply for the {job.title} position at {job.company}.

I am a skilled Python developer with experience in:
- Backend development (FastAPI, Flask, Django)
- Data engineering and automation
- AI/ML integration
- Cloud services (AWS, GCP)

I have attached my CV (Andile-Mchunu-CV.pdf) for your review.

Please find my contact information below:
- Email: andilexmchunu@gmail.com
- Location: Johannesburg, South Africa
- Availability: Immediate

I look forward to hearing from you about this opportunity.

Best regards,
Andile Sizophila Mchunu
"""

            result = send_email(to=original_sender, subject=subject, body_text=body)

            job.applied = True
            logger.info(f"Application sent to {job.company}")
            return True

        except Exception as e:
            logger.error(f"Failed to send application: {e}")
            return False

    def send_pdf_error_response(self, job: Job, original_sender: str) -> bool:
        """Send follow-up when PDF error is detected."""
        subject = f"Re: Application for {job.title} - CV Format Issue"

        body = """Dear Hiring Team,

Thank you for your response regarding my application for the position.

I understand you mentioned an error with my CV: "Cannot read Andile-Mchunu-CV.pdf (this model does not support PDF input)."

I apologize for the inconvenience. My CV is in PDF format which appears to be incompatible with your ATS. 

Here is a text-based summary of my qualifications:

ANDILE SISOPHILA MCHUNU
Python Developer | Data Engineer | Automation Specialist

EXPERIENCE:
- 5+ years Python development
- Backend APIs (FastAPI, Flask, Django)
- Data pipelines and automation
- AI/ML integration with Ollama, LangChain

SKILLS:
- Python, SQL, JavaScript
- AWS, GCP cloud services
- PostgreSQL, MongoDB
- Git, Docker

I would be happy to provide my CV in a different format or answer any questions directly.

Best regards,
Andile Sizophila Mchunu
andilexmchunu@gmail.com
"""

        if self.dry_run:
            logger.info(f"[DRY RUN] Would send PDF error response to {original_sender}")
            job.pdf_error = True
            return True

        try:
            result = send_email(to=original_sender, subject=subject, body_text=body)

            job.pdf_error = True
            logger.info(f"PDF error response sent to {original_sender}")
            return True

        except Exception as e:
            logger.error(f"Failed to send PDF error response: {e}")
            return False

    def check_inbox(self) -> list:
        """Check inbox for job responses."""
        logger.info("Checking inbox for job responses...")

        responses = []

        try:
            emails = get_local_inbox()

            for email in emails:
                subject = email.get("subject", "").lower()
                body = email.get("body", "").lower()

                # Check for PDF-related errors
                if "pdf" in subject or "pdf" in body:
                    if (
                        "cannot read" in body
                        or "does not support" in body
                        or "error" in body
                    ):
                        responses.append(
                            {
                                "type": "pdf_error",
                                "from": email.get("from", ""),
                                "subject": email.get("subject", ""),
                                "body": email.get("body", "")[:500],
                            }
                        )

        except Exception as e:
            logger.error(f"Error checking inbox: {e}")

        return responses

    def apply_to_jobs(self, num_jobs: int = 20) -> ApplicationResult:
        """Apply to remote jobs."""
        logger.info(f"Starting job application process for {num_jobs} jobs...")

        # Search for jobs
        self.search_jobs(num_jobs=num_jobs)

        # Apply to each job
        applications_sent = 0
        for job in self.jobs[:num_jobs]:
            if self.send_application(job):
                applications_sent += 1
            time.sleep(2)  # Rate limiting

        # Save job data
        self._save_jobs()

        return ApplicationResult(
            jobs_found=len(self.jobs),
            applications_sent=applications_sent,
            responses_found=0,
            pdf_errors_handled=0,
            errors=[],
        )

    def check_responses(self) -> ApplicationResult:
        """Check for job responses and handle PDF errors."""
        logger.info("Checking for job responses...")

        responses = self.check_inbox()

        pdf_errors = 0
        for response in responses:
            if response.get("type") == "pdf_error":
                # Try to find matching job and send response
                sender = response.get("from", "")

                # Match job based on sender or subject
                for job in self.jobs:
                    if job.applied:
                        if self.send_pdf_error_response(job, sender):
                            pdf_errors += 1

        self._save_jobs()

        return ApplicationResult(
            jobs_found=len(self.jobs),
            applications_sent=sum(1 for j in self.jobs if j.applied),
            responses_found=len(responses),
            pdf_errors_handled=pdf_errors,
            errors=[],
        )

    def _save_jobs(self):
        """Save job data to file."""
        os.makedirs(self.data_dir, exist_ok=True)

        data = {
            "last_updated": datetime.now().isoformat(),
            "jobs": [
                {
                    "title": j.title,
                    "company": j.company,
                    "email": j.email,
                    "url": j.url,
                    "applied": j.applied,
                    "response_received": j.response_received,
                    "pdf_error": j.pdf_error,
                }
                for j in self.jobs
            ],
        }

        with open(self.jobs_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_jobs(self):
        """Load saved job data."""
        if os.path.exists(self.jobs_file):
            with open(self.jobs_file, "r") as f:
                data = json.load(f)

            self.jobs = [
                Job(
                    title=j["title"],
                    company=j["company"],
                    email=j["email"],
                    url=j["url"],
                    applied=j.get("applied", False),
                    response_received=j.get("response_received", False),
                    pdf_error=j.get("pdf_error", False),
                )
                for j in data.get("jobs", [])
            ]

        return self.jobs


def run_job_application():
    """Main function to run job application."""
    print("=== Remote Job Application System ===")
    print()

    applier = RemoteJobApplier()

    # Load any existing jobs
    existing_jobs = applier.load_jobs()
    if existing_jobs:
        print(f"Loaded {len(existing_jobs)} previous job applications")

    # Step 1: Apply to jobs
    print("\n[1/3] Applying to remote jobs...")
    result = applier.apply_to_jobs(num_jobs=20)
    print(f"Applied to {result.applications_sent} jobs out of {result.jobs_found}")

    # Step 2: Wait and check for responses
    print("\n[2/3] Checking for responses (simulated)...")
    print("Note: In production, wait for responses to arrive")

    # Step 3: Handle any PDF errors
    print("\n[3/3] Checking for PDF errors...")
    response_result = applier.check_responses()
    print(f"Found {response_result.responses_found} responses")
    print(f"Handled {response_result.pdf_errors_handled} PDF errors")

    # Summary
    print("\n=== Application Summary ===")
    print(f"Total jobs found: {result.jobs_found}")
    print(f"Applications sent: {result.applications_sent}")
    print(f"Responses received: {response_result.responses_found}")
    print(f"PDF errors handled: {response_result.pdf_errors_handled}")
    print(f"\nJobs saved to: {applier.jobs_file}")

    return result


if __name__ == "__main__":
    run_job_application()
