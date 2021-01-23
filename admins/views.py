from .forms import AuthForm, PatientForm, CaseCreationForm, CaseEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from patients.models import Cases, Patient
from .utils import validate_access
from doctors.models import Doctor
from .models import Staff
import json


# staff attendance
@login_required()
def attendance(request):

    # Checking if the user is an Admin member
    validate_access(request, 'a')

    # Getting the list of doctors
    doctors = Staff.objects.filter(role='d')

    # Checking if update is available
    if "update" in request.GET:

        # Getting the attendance from the request
        data = json.loads(request.GET["attendance"])

        # Updating the doctor attendance
        for doc in data:
            doctor = doctors.get(id=int(doc)).doctor
            doctor.availability = data[doc]
            doctor.save()

        # Returning the success message
        return HttpResponse("Success!")

    return render(request, "admins/attendance.html", context={'doctors': doctors})


# Patient Creation Page
@login_required()
def create_patient(request):
    validate_access(request, 'a')

    # if form data provided
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    form = PatientForm()
    return render(request, "admins/create_patient.html", context={'form': form, 'title': "Create"})


# Patient Creation Page
@login_required()
def edit_patient(request):
    validate_access(request, 'a')
    # Getting the required patient object
    patient = Patient.objects.get(id=int(request.GET["id"]))

    # If form data provided
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect("home")

    # Populating the fields with default values
    gender = patient.gender.upper()
    form = PatientForm(data={'name': patient.name, 'age': patient.age, "phone": patient.phone,
                             'gender': gender, 'blood_type': patient.blood_type,
                             "email": patient.email})

    return render(request, "admins/create_patient.html", context={'form': form, 'title': "Edit"})


# Create case
@login_required()
def create_case(request):
    validate_access(request, 'a')

    if request.method == "POST":
        form = CaseCreationForm(request.POST)
        form.set_choices()

        # Checking if the input is valid
        if form.is_valid():
            data = form.cleaned_data
            doctor = Doctor.objects.get(id=int(data['doctor']))
            patient = Patient.objects.get(id=int(data['patient']))
            case = Cases(doctor=doctor, patient=patient, status='t',
                         appointed_date=data['date'], state=data['state'])
            case.save()
            return redirect("home")

    form = CaseCreationForm()
    form.set_choices()
    return render(request, "admins/create_case.html", context={'form': form, 'title': "Create"})


# Create case
@login_required()
def edit_case(request):
    validate_access(request, 'a')
    case = Cases.objects.get(id=int(request.GET['id']))

    if request.method == "POST":
        form = CaseEditForm(request.POST)
        form.set_choices()
        # Checking if the input is valid
        if form.is_valid():
            data = form.cleaned_data
            doctor = Doctor.objects.get(id=int(data['doctor']))
            patient = Patient.objects.get(id=int(data['patient']))
            print(data)

            # Saving the case info
            case.doctor = doctor
            case.patient = patient
            case.status = 't'
            case.appointed_date = data['date']
            case.state = data['state']
            case.save()
            return redirect("home")

    date = case.appointed_date.strftime('%d/%m/%Y %H:%M')
    print(date)
    form = CaseEditForm(initial={'patient': case.patient.id, 'doctor': case.doctor.id,
                                 'state': case.state, 'date': date})
    form.set_choices()
    form.set_patient([case.patient])
    return render(request, "admins/create_case.html", context={'form': form, 'title': "Edit"})


# list patients
@login_required()
def list_patients(request):
    validate_access(request, 'a')
    patients = Patient.objects.all()
    return render(request, "admins/list_patients.html", context={'patients': patients})


# list cases
@login_required()
def list_cases(request):
    validate_access(request, 'a')
    cases = Cases.objects.filter(status='t')

    # Checking if the case is to be deleted
    if 'delete_id' in request.GET:
        case = cases.get(id=int(request.GET['delete_id']))
        case.delete()

    return render(request, "admins/list_cases.html", context={'cases': cases})


""" <===========================|******| Base Routes |******|===========================> """


# login page
class LoginView(auth_views.LoginView):
    form_class = AuthForm


# Confirm Logout page
def confirm_logout(request):
    return render(request, "admins/confirm_logout.html")


# login redirect
@login_required()
def redirect_login(request):
    user = User.objects.get(username=request.user)
    if user.staff.role == "d":
        return redirect('doctor:dashboard')
    elif user.staff.role == "a":
        return redirect('home')
    elif user.staff.role == "p":
        return redirect('pharma:shop')
    elif user.staff.role == 'ac':
        return redirect('accounts:dashboard')
    else:
        raise Http404("page not found")


# Edit the function below.
def home(request):
    return render(request, "admins/home.html")


# Setting the theme for the site
def set_theme(request):
    theme = request.COOKIES.get('theme')
    if not theme:
        theme = 'w'
    elif theme == 'w':
         theme = 'd'
    else:
        theme = 'w'
    response = HttpResponse('set theme')
    response.set_cookie('theme', theme)
    return response
