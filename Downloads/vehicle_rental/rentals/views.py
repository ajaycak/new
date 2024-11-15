from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import models
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Booking, Payment, Vehicle, VehicleRequest, ContactMessage
from .forms import CustomUserRegistrationForm, BookingForm, VehicleRequestForm

# View to display vehicle details and handle bookings
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    filled_stars = range(vehicle.rating)
    empty_stars = range(5 - vehicle.rating)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.vehicle = vehicle

            if is_vehicle_available(vehicle, booking.booking_date, booking.return_date):
                booking.save()
                vehicle.availability = False
                vehicle.save()
                return redirect('booking_success')
            else:
                form.add_error(None, "This vehicle is not available for the selected dates.")
    else:
        form = BookingForm()

    return render(request, 'rentals/vehicle_detail.html', {
        'vehicle': vehicle,
        'form': form,
        'filled_stars': filled_stars,
        'empty_stars': empty_stars,
    })

# Helper function to check vehicle availability
def is_vehicle_available(vehicle, start_date, end_date):
    bookings = Booking.objects.filter(vehicle=vehicle)
    for booking in bookings:
        if (start_date <= booking.return_date and end_date >= booking.booking_date):
            return False
    return True

# Home page showing all vehicles and user bookings
def home(request):
    vehicles = Vehicle.objects.all()
    bookings = Booking.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'home.html', {'vehicles': vehicles, 'bookings': bookings})

def about(request):
    return render(request, 'rentals/about.html')


# User registration view
from .forms import CustomUserRegistrationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserRegistrationForm


def custom_register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Make sure this is called correctly
            return redirect('login')  # Or whatever page you want to redirect to after successful registration
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


# User login view
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'rentals/login.html', {'form': form})

# User logout view
def custom_logout(request):
    logout(request)
    return redirect('home')

# Booking detail view
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_detail.html', {'booking': booking})

# Success page after booking
def booking_success(request):
    return render(request, 'rentals/booking_success.html')

# Vehicle request view (for adding new vehicle requests)
@login_required
def vehicle_request_view(request):
    if request.method == 'POST':
        form = VehicleRequestForm(request.POST)
        if form.is_valid():
            vehicle_request = form.save(commit=False)
            vehicle_request.user = request.user
            vehicle_request.save()
            return redirect('vehicle_request_success')
    else:
        form = VehicleRequestForm()
    return render(request, 'rentals/vehicle_request_form.html', {'form': form})

# Success page for vehicle request submission
def request_success_view(request):
    return render(request, 'rentals/request_success.html')

# View to list all vehicle requests
def vehicle_request_list_view(request):
    vehicle_requests = VehicleRequest.objects.all()
    return render(request, 'rentals/vehicle_request_list.html', {'vehicle_requests': vehicle_requests})

# View to handle vehicle list, including recommended vehicles
def vehicle_list(request):
    recommended_vehicle = Vehicle.objects.filter(is_recommended=True).first()
    other_vehicles = Vehicle.objects.exclude(is_recommended=True)
    context = {
        'recommended_vehicle': recommended_vehicle,
        'other_vehicles': other_vehicles
    }
    return render(request, 'rentals/vehicles_list.html', context)

@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        # Assuming the payment form has fields for amount, payment_method, etc.
        payment_method = request.POST.get('payment_method', 'Card')  # example default
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.vehicle.price,
            payment_date=date.today(),
            status="Paid",
            payment_method=payment_method,
        )
        booking.status = "Paid"
        booking.save()
        messages.success(request, "Payment successful and booking updated.")
        return redirect('booking_detail', booking_id=booking.id)  # Redirect to a booking detail view
    
    return render(request, 'rentals/payment_form.html', {'booking': booking})

# Handle vehicle request approval
@require_POST
def approve_vehicle_request(request, request_id):
    vehicle_request = get_object_or_404(VehicleRequest, id=request_id)
    Vehicle.objects.create(
        vehicle_type=vehicle_request.vehicle_type,
        model=vehicle_request.model,
        price=vehicle_request.price,
    )
    vehicle_request.status = 'Approved'
    vehicle_request.save()

    messages.success(request, "Vehicle request approved and added to the site.")
    return HttpResponseRedirect(reverse('vehicle_request_list'))

# Handle vehicle request rejection
@require_POST
def reject_vehicle_request(request, request_id):
    vehicle_request = get_object_or_404(VehicleRequest, id=request_id)
    vehicle_request.delete()

    messages.success(request, "Vehicle request rejected and removed.")
    return HttpResponseRedirect(reverse('vehicle_request_list'))

# Contact page to send messages
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, "Your message has been sent!")
        return redirect('contact')
    return render(request, 'rentals/contact.html')
