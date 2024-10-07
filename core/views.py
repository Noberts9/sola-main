from django.shortcuts import render, redirect
from item.models import Category, Item
from .forms import SignupForm
from django.contrib.auth.models import User
from django.conf import settings
import africastalking
import random

# Initialize Africa's Talking API
africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms = africastalking.SMS

# Generate a random OTP
def generate_otp():
    return random.randint(100000, 999999)

# Send OTP via Africa's Talking
def send_otp(phone_number, otp):
    message = f"Your OTP code is {otp}."
    sms.send(message, [phone_number])

# View for signup and sending OTP
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)  # Save user but don't commit yet
            user.is_active = False  # Deactivate user until OTP is verified
            user.save()

            # Generate and send OTP
            otp = generate_otp()
            request.session['otp'] = otp  # Store OTP in session
            request.session['user_id'] = user.id  # Store user ID in session
            send_otp(form.cleaned_data['phone_number'], otp)

            return redirect('verify_otp')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})

# View for OTP verification
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        if entered_otp == str(request.session.get('otp')):
            # OTP is valid, activate the user
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            # Clear session data
            del request.session['otp']
            del request.session['user_id']

            return redirect('login')
        else:
            return render(request, 'core/verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'core/verify_otp.html')

# Index view (unchanged)
def index(request):
    items = Item.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()

    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items,
    })

# Contact view (unchanged)
def contact(request):
    return render(request, 'core/contact.html')
