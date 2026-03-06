# Placement Portal Application

A Flask-based web application to manage campus recruitment activities between students, companies, and the institute placement cell.

## Tech Stack
- Flask
- Jinja2 Templates
- SQLite
- Bootstrap

## Roles
### Admin (Placement Cell)
- Approve/reject company registrations
- Approve/reject placement drives
- View statistics (students, companies, drives, applications)

### Company
- Register and wait for admin approval
- Create and manage placement drives
- View applicants
- Download resumes
- Update application status

### Student
- Register and login
- View approved placement drives
- Apply for jobs (resume required per application)
- Track application status

## Features
- Role-based authentication
- Company approval system
- Placement drive management
- Resume upload for each application
- Duplicate application prevention
- Applicant status tracking

## Run the project locally

Clone the repo:

```bash
git clone https://github.com/Gbsayee07/placement-portal-flask.git
cd placement-portal-flask
