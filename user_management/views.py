from django.shortcuts import render, redirect, get_object_or_404
from .models import Person
from .forms import PersonForm
from .tasks import send_welcome_email


# Get all users
def person_list(request):
    persons = Person.objects.all()
    return render(request, 'person_list.html', {'persons': persons})


# Create new user
def person_create(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save()

            send_welcome_email.delay(
                from_email='noreply-crud@gmail.com',
                to_email=person.email,
                subject='Welcome to our website!',
                message=f'Hello, {person.name}! \
                    Thank you for joining our community.'
            )

            return redirect('person_list')
    else:
        form = PersonForm()

    return render(request, 'person_form.html', {'form': form})


# Update user
def person_update(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            return redirect('person_list')
    else:
        form = PersonForm(instance=person)
    return render(request, 'person_form.html', {'form': form})


# Delete user
def person_delete(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.method == 'POST':
        person.delete()
        return redirect('person_list')
    return render(request, 'person_delete.html', {'person': person})
