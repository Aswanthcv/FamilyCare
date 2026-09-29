# FamilyCare — Family Health Record Management System

FamilyCare is a Django-based web application for managing health records of multiple family members from a single family account.

The application allows a family to maintain member profiles and securely manage medical information such as test results, medical reports, doctor visits, prescriptions, insurance details, and other medical documents.

> **Note:** FamilyCare is a record-management system for educational purposes. It does not provide medical diagnosis or treatment recommendations.

## Features

- Family account registration and login
- Secure logout and session-based authentication
- Add, edit, view, and delete family members
- Family member health profiles
- Blood group, height, weight, medical conditions, allergies, and medications
- Test result management
- Medical report management
- Doctor visit records
- Prescription records
- Insurance information
- Other medical document uploads
- PDF, JPG, and PNG file validation
- Protected medical file access
- Health timeline for each family member
- Ownership-based access control
- Form validation
- Django messages and user-friendly UI
- Automated tests
- GitHub Actions CI

## How It Works

The application follows a simple ownership structure:

```text
Family Account (Django User)
        │
        ├── Family Member
        │       ├── Test Results
        │       ├── Medical Reports
        │       ├── Doctor Visits
        │       ├── Prescriptions
        │       ├── Insurance
        │       └── Medical Documents
        │
        └── Family Member
                └── Health Records
```

A family account can manage its own family members and their records.

For example:

```text
Nair Family
    │
    ├── Father
    │    ├── Test Results
    │    └── Prescriptions
    │
    ├── Mother
    │    ├── Doctor Visits
    │    └── Medical Reports
    │
    └── Son
         └── Test Results
```

Different family accounts cannot access each other's family members or medical records.

## Security

FamilyCare uses Django's built-in authentication and ownership checks.

Examples of protection include:

- Login required for private pages
- Family-member ownership verification
- Record ownership verification through the related family member
- Protected medical file views
- CSRF protection
- Django's built-in password hashing
- File type validation
- Users cannot access another family's records by changing an object ID in the URL

Example ownership check:

```python
get_object_or_404(
    FamilyMember,
    id=member_id,
    user=request.user
)
```

For a medical record:

```python
get_object_or_404(
    MedicalReport,
    id=report_id,
    family_member__user=request.user
)
```

## Health Timeline

The member profile includes a chronological health timeline.

The timeline combines existing records such as:

- Test results
- Medical reports
- Doctor visits
- Prescriptions
- Insurance records
- Medical documents

The records are sorted by date so that the family can see a member's health history in one place.

No separate timeline database model is required.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Django | Web framework |
| Django Templates | Frontend rendering |
| HTML | Page structure |
| CSS | Styling |
| SQLite | Development database |
| Pillow | Image processing |
| Git | Version control |
| GitHub | Source code hosting |
| GitHub Actions | Continuous Integration |

## Project Structure

```text
FamilyCare/
│
├── familycare/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── records/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── tests.py
│   └── ...
│
├── templates/
│   ├── registration/
│   └── ...
│
├── static/
│
├── media/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── .github/
    └── workflows/
        └── ci.yml
```

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd FamilyCare
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Running Tests

Run the complete test suite:

```bash
python manage.py test
```

Current test status:

```text
18 tests passed
```

You can also run Django's system checks:

```bash
python manage.py check
```

## Continuous Integration

FamilyCare uses GitHub Actions for Continuous Integration.

The workflow runs automatically when code is:

- Pushed to the repository
- Submitted through a pull request

The CI pipeline:

```text
Push / Pull Request
        ↓
Checkout Repository
        ↓
Set up Python 3.13
        ↓
Install Dependencies
        ↓
Django Check
        ↓
Run Tests
        ↓
Pass / Fail
```

Workflow file:

```text
.github/workflows/ci.yml
```

## Database Relationships

The main relationship is:

```text
User
 │
 └── FamilyMember
       │
       ├── TestResult
       ├── MedicalReport
       ├── DoctorVisit
       ├── Prescription
       ├── Insurance
       └── MedicalDocument
```

Each health record belongs to a specific family member, and each family member belongs to a specific authenticated family account.

## Future Improvements

Possible future improvements include:

- PostgreSQL for production
- Cloud-based file storage
- Stronger production security configuration
- Audit logs
- Email notifications
- Automated deployment
- Docker containerization
- Role-based permissions
- Backup and recovery system

## Disclaimer

This project is intended for learning and demonstration purposes.

It is not designed to replace professional medical systems, electronic health record platforms, or medical advice.

Do not upload real sensitive medical information to an unsecured development deployment.

## Author

**Aswanth**

Built as a Django learning and portfolio project.
