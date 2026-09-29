from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from io import BytesIO
from PIL import Image

from .models import DoctorVisit, FamilyMember, Insurance, MedicalDocument, MedicalReport, Prescription, TestResult

class AuthenticationTests(TestCase):
    def setUp(self):
        self.password = 'Strong-password-123'
        self.user = User.objects.create_user(username='family-one', email='family@example.com', password=self.password)

    def test_dashboard_redirects_anonymous_users_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')

    def test_registration_creates_user_and_logs_them_in(self):
        response = self.client.post('/register/', {
            'username': 'new-family', 'email': 'new@example.com',
            'password1': 'Another-strong-password-123',
            'password2': 'Another-strong-password-123',
        })
        self.assertRedirects(response, '/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(User.objects.filter(username='new-family').exists())

    def test_login_and_logout_work(self):
        response = self.client.post('/login/', {'username': 'family-one', 'password': self.password})
        self.assertRedirects(response, '/')
        response = self.client.get('/')
        self.assertContains(response, 'Welcome, family-one!')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/')
        self.assertNotIn('_auth_user_id', self.client.session)


class FamilyMemberTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='other', password='Strong-password-123')
        self.client.force_login(self.user)

    def member_data(self):
        image_buffer = BytesIO()
        Image.new('RGB', (10, 10), color='blue').save(image_buffer, format='JPEG')
        image = SimpleUploadedFile('profile.jpg', image_buffer.getvalue(), content_type='image/jpeg')
        return {
            'full_name': 'Asha Owner', 'date_of_birth': '1990-05-10', 'sex': 'F',
            'phone': '1234567890', 'email': 'asha@example.com', 'profile_image': image,
            'blood_group': 'O+', 'height': '165', 'weight': '60',
            'medical_conditions': 'None', 'allergies': 'None',
            'current_medications': '', 'emergency_contact': '9999999999', 'additional_notes': '',
        }

    def test_add_view_edit_and_delete_member(self):
        response = self.client.post('/members/add/', self.member_data())
        self.assertEqual(response.status_code, 302)
        member = FamilyMember.objects.get(full_name='Asha Owner')
        self.assertEqual(member.user, self.user)
        self.assertTrue(member.profile_image.name.startswith('profile_images/'))

        self.assertEqual(self.client.get(f'/members/{member.id}/').status_code, 200)
        response = self.client.post(f'/members/{member.id}/edit/', {
            **self.member_data(), 'profile_image': '', 'full_name': 'Asha Updated',
        })
        self.assertEqual(response.status_code, 302)
        member.refresh_from_db()
        self.assertEqual(member.full_name, 'Asha Updated')

        self.assertEqual(self.client.get(f'/members/{member.id}/delete/').status_code, 200)
        response = self.client.post(f'/members/{member.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FamilyMember.objects.filter(id=member.id).exists())

    def test_user_cannot_access_another_users_member(self):
        member = FamilyMember.objects.create(
            user=self.other_user, full_name='Other Person', date_of_birth='2000-01-01', sex='O',
        )
        self.assertEqual(self.client.get(f'/members/{member.id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/members/{member.id}/edit/').status_code, 404)
        self.assertEqual(self.client.get(f'/members/{member.id}/delete/').status_code, 404)


class TestResultTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test-owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='test-other', password='Strong-password-123')
        self.member = FamilyMember.objects.create(
            user=self.user, full_name='Test Member', date_of_birth='1990-01-01', sex='O',
        )
        self.client.force_login(self.user)

    def result_data(self):
        return {
            'test_name': 'Blood Test', 'test_date': '2025-01-15',
            'laboratory_or_hospital': 'City Hospital', 'result_summary': 'All normal',
        }

    def test_create_view_edit_delete_and_file_upload(self):
        report = SimpleUploadedFile('blood-test.pdf', b'%PDF-demo', content_type='application/pdf')
        response = self.client.post(
            f'/members/{self.member.id}/tests/add/',
            {**self.result_data(), 'report_file': report},
        )
        self.assertEqual(response.status_code, 302)
        result = TestResult.objects.get(test_name='Blood Test')
        self.assertEqual(result.family_member, self.member)
        self.assertTrue(result.report_file.name.startswith('test_reports/'))

        response = self.client.get(f'/members/{self.member.id}/')
        self.assertContains(response, 'Blood Test')
        response = self.client.get(f'/test-results/{result.id}/report/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(f'/test-results/{result.id}/edit/', {
            **self.result_data(), 'test_name': 'Updated Blood Test', 'report_file': '',
        })
        self.assertEqual(response.status_code, 302)
        result.refresh_from_db()
        self.assertEqual(result.test_name, 'Updated Blood Test')

        self.assertEqual(self.client.get(f'/test-results/{result.id}/delete/').status_code, 200)
        response = self.client.post(f'/test-results/{result.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TestResult.objects.filter(id=result.id).exists())

    def test_user_cannot_access_another_users_test_result(self):
        other_member = FamilyMember.objects.create(
            user=self.other_user, full_name='Other Member', date_of_birth='1990-01-01', sex='O',
        )
        result = TestResult.objects.create(
            family_member=other_member, test_name='Private Test', test_date='2025-01-01',
        )
        self.assertEqual(self.client.get(f'/test-results/{result.id}/edit/').status_code, 404)
        self.assertEqual(self.client.get(f'/test-results/{result.id}/delete/').status_code, 404)
        self.assertEqual(self.client.get(f'/test-results/{result.id}/report/').status_code, 404)


class MedicalReportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='report-owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='report-other', password='Strong-password-123')
        self.member = FamilyMember.objects.create(
            user=self.user, full_name='Report Member', date_of_birth='1990-01-01', sex='O',
        )
        self.client.force_login(self.user)

    def report_data(self):
        return {
            'report_title': 'Cardiology Report', 'report_date': '2025-02-20',
            'hospital_or_clinic': 'Heart Clinic', 'doctor_name': 'Dr. Rao',
            'notes': 'Follow-up recommended',
        }

    def test_create_view_edit_delete_and_file_upload(self):
        report_file = SimpleUploadedFile('cardiology.pdf', b'%PDF-demo', content_type='application/pdf')
        response = self.client.post(
            f'/members/{self.member.id}/medical-reports/add/',
            {**self.report_data(), 'report_file': report_file},
        )
        self.assertEqual(response.status_code, 302)
        report = MedicalReport.objects.get(report_title='Cardiology Report')
        self.assertEqual(report.family_member, self.member)
        self.assertTrue(report.report_file.name.startswith('medical_reports/'))

        response = self.client.get(f'/members/{self.member.id}/')
        self.assertContains(response, 'Cardiology Report')
        response = self.client.get(f'/medical-reports/{report.id}/report/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(f'/medical-reports/{report.id}/edit/', {
            **self.report_data(), 'report_title': 'Updated Cardiology Report', 'report_file': '',
        })
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.report_title, 'Updated Cardiology Report')

        self.assertEqual(self.client.get(f'/medical-reports/{report.id}/delete/').status_code, 200)
        response = self.client.post(f'/medical-reports/{report.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MedicalReport.objects.filter(id=report.id).exists())

    def test_user_cannot_access_another_users_medical_report(self):
        other_member = FamilyMember.objects.create(
            user=self.other_user, full_name='Other Report Member', date_of_birth='1990-01-01', sex='O',
        )
        report = MedicalReport.objects.create(
            family_member=other_member, report_title='Private Report', report_date='2025-01-01',
        )
        self.assertEqual(self.client.get(f'/medical-reports/{report.id}/edit/').status_code, 404)
        self.assertEqual(self.client.get(f'/medical-reports/{report.id}/delete/').status_code, 404)
        self.assertEqual(self.client.get(f'/medical-reports/{report.id}/report/').status_code, 404)


class DoctorVisitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='visit-owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='visit-other', password='Strong-password-123')
        self.member = FamilyMember.objects.create(
            user=self.user, full_name='Visit Member', date_of_birth='1990-01-01', sex='O',
        )
        self.client.force_login(self.user)

    def visit_data(self):
        return {
            'doctor_name': 'Dr. Menon', 'hospital_or_clinic': 'City Clinic',
            'visit_date': '2025-03-10', 'reason_for_visit': 'Regular check-up',
            'diagnosis_or_condition': 'Healthy', 'doctor_notes': 'Continue exercise',
            'follow_up_date': '2025-09-10',
        }

    def test_create_view_edit_delete_and_optional_document(self):
        document = SimpleUploadedFile('visit-note.jpg', b'fake-jpg', content_type='image/jpeg')
        response = self.client.post(
            f'/members/{self.member.id}/doctor-visits/add/',
            {**self.visit_data(), 'visit_document': document},
        )
        self.assertEqual(response.status_code, 302)
        visit = DoctorVisit.objects.get(doctor_name='Dr. Menon')
        self.assertEqual(visit.family_member, self.member)
        self.assertTrue(visit.visit_document.name.startswith('visit_documents/'))

        response = self.client.get(f'/members/{self.member.id}/')
        self.assertContains(response, 'Dr. Menon')
        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/').status_code, 200)
        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/document/').status_code, 200)

        response = self.client.post(f'/doctor-visits/{visit.id}/edit/', {
            **self.visit_data(), 'doctor_name': 'Dr. Updated', 'visit_document': '',
        })
        self.assertEqual(response.status_code, 302)
        visit.refresh_from_db()
        self.assertEqual(visit.doctor_name, 'Dr. Updated')

        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/delete/').status_code, 200)
        response = self.client.post(f'/doctor-visits/{visit.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DoctorVisit.objects.filter(id=visit.id).exists())

    def test_user_cannot_access_another_users_visit(self):
        other_member = FamilyMember.objects.create(
            user=self.other_user, full_name='Other Visit Member', date_of_birth='1990-01-01', sex='O',
        )
        visit = DoctorVisit.objects.create(
            family_member=other_member, doctor_name='Private Doctor', visit_date='2025-01-01',
        )
        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/edit/').status_code, 404)
        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/delete/').status_code, 404)
        self.assertEqual(self.client.get(f'/doctor-visits/{visit.id}/document/').status_code, 404)


class PrescriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='prescription-owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='prescription-other', password='Strong-password-123')
        self.member = FamilyMember.objects.create(
            user=self.user, full_name='Prescription Member', date_of_birth='1990-01-01', sex='O',
        )
        self.client.force_login(self.user)

    def prescription_data(self):
        return {
            'doctor_name': 'Dr. Joseph', 'prescription_date': '2025-04-12',
            'medicines': 'Medicine A, Medicine B', 'dosage_instructions': 'Twice daily',
            'duration': '7 days',
        }

    def test_create_view_edit_delete_and_optional_file_upload(self):
        prescription_file = SimpleUploadedFile('prescription.png', b'fake-png', content_type='image/png')
        response = self.client.post(
            f'/members/{self.member.id}/prescriptions/add/',
            {**self.prescription_data(), 'prescription_file': prescription_file},
        )
        self.assertEqual(response.status_code, 302)
        prescription = Prescription.objects.get(doctor_name='Dr. Joseph')
        self.assertEqual(prescription.family_member, self.member)
        self.assertTrue(prescription.prescription_file.name.startswith('prescriptions/'))

        response = self.client.get(f'/members/{self.member.id}/')
        self.assertContains(response, 'Dr. Joseph')
        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/').status_code, 200)
        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/file/').status_code, 200)

        response = self.client.post(f'/prescriptions/{prescription.id}/edit/', {
            **self.prescription_data(), 'doctor_name': 'Dr. Updated', 'prescription_file': '',
        })
        self.assertEqual(response.status_code, 302)
        prescription.refresh_from_db()
        self.assertEqual(prescription.doctor_name, 'Dr. Updated')

        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/delete/').status_code, 200)
        response = self.client.post(f'/prescriptions/{prescription.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Prescription.objects.filter(id=prescription.id).exists())

    def test_user_cannot_access_another_users_prescription(self):
        other_member = FamilyMember.objects.create(
            user=self.other_user, full_name='Other Prescription Member', date_of_birth='1990-01-01', sex='O',
        )
        prescription = Prescription.objects.create(
            family_member=other_member, doctor_name='Private Doctor', prescription_date='2025-01-01', medicines='Private medicine',
        )
        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/').status_code, 404)
        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/edit/').status_code, 404)
        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/delete/').status_code, 404)
        self.assertEqual(self.client.get(f'/prescriptions/{prescription.id}/file/').status_code, 404)


class InsuranceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='insurance-owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='insurance-other', password='Strong-password-123')
        self.member = FamilyMember.objects.create(user=self.user, full_name='Insurance Member', date_of_birth='1990-01-01', sex='O')
        self.client.force_login(self.user)

    def data(self):
        return {'provider_name': 'Health Cover', 'policy_number': 'POL-123', 'member_id': 'MEM-123', 'start_date': '2025-01-01', 'expiry_date': '2026-01-01', 'notes': 'Main policy'}

    def test_insurance_crud_file_and_ownership(self):
        card = SimpleUploadedFile('card.pdf', b'%PDF-card', content_type='application/pdf')
        response = self.client.post(f'/members/{self.member.id}/insurance/add/', {**self.data(), 'insurance_card': card})
        self.assertEqual(response.status_code, 302)
        insurance = Insurance.objects.get(provider_name='Health Cover')
        self.assertTrue(insurance.insurance_card.name.startswith('insurance_cards/'))
        self.assertContains(self.client.get(f'/members/{self.member.id}/'), 'Health Cover')
        self.assertEqual(self.client.get(f'/insurance/{insurance.id}/').status_code, 200)
        self.assertEqual(self.client.get(f'/insurance/{insurance.id}/card/').status_code, 200)
        self.assertEqual(self.client.post(f'/insurance/{insurance.id}/edit/', {**self.data(), 'provider_name': 'Updated Cover', 'insurance_card': ''}).status_code, 302)
        insurance.refresh_from_db()
        self.assertEqual(insurance.provider_name, 'Updated Cover')
        self.assertEqual(self.client.get(f'/insurance/{insurance.id}/delete/').status_code, 200)
        self.assertEqual(self.client.post(f'/insurance/{insurance.id}/delete/').status_code, 302)
        self.assertFalse(Insurance.objects.filter(id=insurance.id).exists())

    def test_other_user_cannot_access_insurance(self):
        member = FamilyMember.objects.create(user=self.other_user, full_name='Other', date_of_birth='1990-01-01', sex='O')
        insurance = Insurance.objects.create(family_member=member, provider_name='Private', policy_number='P', member_id='M', start_date='2025-01-01', expiry_date='2026-01-01')
        for url in (f'/insurance/{insurance.id}/', f'/insurance/{insurance.id}/edit/', f'/insurance/{insurance.id}/delete/', f'/insurance/{insurance.id}/card/'):
            self.assertEqual(self.client.get(url).status_code, 404)


class MedicalDocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='document-owner', password='Strong-password-123')
        self.other_user = User.objects.create_user(username='document-other', password='Strong-password-123')
        self.member = FamilyMember.objects.create(user=self.user, full_name='Document Member', date_of_birth='1990-01-01', sex='O')
        self.client.force_login(self.user)

    def data(self):
        return {'title': 'Vaccination Record', 'document_date': '2025-05-01', 'description': 'Vaccination details'}

    def test_document_crud_file_and_ownership(self):
        document_file = SimpleUploadedFile('vaccine.jpg', b'fake-jpg', content_type='image/jpeg')
        response = self.client.post(f'/members/{self.member.id}/documents/add/', {**self.data(), 'document_file': document_file})
        self.assertEqual(response.status_code, 302)
        document = MedicalDocument.objects.get(title='Vaccination Record')
        self.assertTrue(document.document_file.name.startswith('medical_documents/'))
        self.assertContains(self.client.get(f'/members/{self.member.id}/'), 'Vaccination Record')
        self.assertEqual(self.client.get(f'/documents/{document.id}/').status_code, 200)
        self.assertEqual(self.client.get(f'/documents/{document.id}/file/').status_code, 200)
        self.assertEqual(self.client.post(f'/documents/{document.id}/edit/', {**self.data(), 'title': 'Updated Record', 'document_file': ''}).status_code, 302)
        document.refresh_from_db()
        self.assertEqual(document.title, 'Updated Record')
        self.assertEqual(self.client.get(f'/documents/{document.id}/delete/').status_code, 200)
        self.assertEqual(self.client.post(f'/documents/{document.id}/delete/').status_code, 302)
        self.assertFalse(MedicalDocument.objects.filter(id=document.id).exists())

    def test_other_user_cannot_access_document(self):
        member = FamilyMember.objects.create(user=self.other_user, full_name='Other', date_of_birth='1990-01-01', sex='O')
        document = MedicalDocument.objects.create(family_member=member, title='Private', document_date='2025-01-01', document_file=SimpleUploadedFile('private.pdf', b'%PDF'))
        for url in (f'/documents/{document.id}/', f'/documents/{document.id}/edit/', f'/documents/{document.id}/delete/', f'/documents/{document.id}/file/'):
            self.assertEqual(self.client.get(url).status_code, 404)


class TimelineTests(TestCase):
    def test_member_profile_shows_timeline_records(self):
        user = User.objects.create_user(username='timeline-user', password='Strong-password-123')
        member = FamilyMember.objects.create(user=user, full_name='Timeline Member', date_of_birth='1990-01-01', sex='O')
        TestResult.objects.create(family_member=member, test_name='Blood Test', test_date='2025-01-01')
        DoctorVisit.objects.create(family_member=member, doctor_name='Dr. Timeline', visit_date='2025-02-01')
        self.client.force_login(user)
        response = self.client.get(f'/members/{member.id}/')
        self.assertContains(response, 'Health Timeline')
        self.assertContains(response, 'Blood Test')
        self.assertContains(response, 'Dr. Timeline')
