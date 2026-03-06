# Placement Portal Application

A Flask-based web application for managing campus recruitment activities between students, companies, and the institute placement cell.

The system allows companies to create placement drives, students to apply for them, and the admin (placement cell) to manage approvals and track recruitment activities.

---

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** Jinja2 Templates, HTML, CSS, Bootstrap
- **Database:** SQLite
- **Authentication:** Flask-Login
- **ORM:** Flask-SQLAlchemy

---

## System Roles

### Admin (Placement Cell)
The admin is the institute placement authority.

Admin can:
- Approve or reject company registrations
- Approve or reject placement drives
- View statistics of students, companies, drives, and applications
- Manage the overall recruitment process

**Default Admin Login**
- Email: `admin@college.com`
- Password: `admin123`

### Company
Companies can:
- Register a company account
- Wait for admin approval
- Create placement drives
- Edit, close, or delete drives
- View students who applied
- Download resumes submitted by students
- Update application status

**Application status options**
- Applied
- Shortlisted
- Selected
- Rejected

### Student
Students can:
- Register and login
- View approved placement drives
- Apply for drives
- Upload a resume for each application
- Track application status

The system prevents duplicate applications for the same drive.

---

## Key Features

- Role-based authentication system
- Company registration approval system
- Placement drive creation and approval
- Resume upload for each job application
- Duplicate application prevention
- Applicant status tracking
- Company applicant management
- Admin dashboard with statistics

---

## Database Structure

Main tables used in the system:
- `users`
- `student_profiles`
- `company_profiles`
- `placement_drives`
- `applications`

Relationships:
- `User` → `StudentProfile`
- `User` → `CompanyProfile`
- `CompanyProfile` → `PlacementDrive`
- `StudentProfile` → `Application`
- `PlacementDrive` → `Application`

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/Gbsayee07/placement-portal-flask.git
cd placement-portal-flask