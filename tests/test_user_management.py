import pytest
from django.urls import reverse
from django.test import Client
from user_management.models import Person

# Fixture for creating a test client


@pytest.fixture
def client():
    return Client()

# Fixture for creating a Person object


@pytest.fixture
def person():
    return Person.objects.create(
        name='Alain',
        age=22,
        email='alainnambi@gmail.com'
    )


@pytest.mark.django_db
def test_person_list(client):
    # Create a few persons
    Person.objects.create(name='John', age=30, email='john@example.com')
    Person.objects.create(name='Jade', age=26, email='jade@example.com')

    # Access the person list view
    response = client.get(reverse('person_list'))

    assert response.status_code == 200

    # Assuming the context contains 'persons' with the list of persons
    # Check if both persons are in the context
    assert len(response.context['persons']) == 2


@pytest.mark.django_db
def test_person_create(client):
    data = {
        'name': 'New Person',
        'age': 25,
        'email': 'newperson@example.com'
    }

    # Access the person create view
    response = client.post(reverse('person_create'), data)
    assert response.status_code == 302  # Redirect to person_list
    # More efficient existence check
    assert Person.objects.filter(name='New Person').exists()


@pytest.mark.django_db
def test_person_update(client, person):
    data = {
        'name': 'Updated Alain',
        'age': 23,
        'email': 'alainnambi@example.com'
    }

    # Access the person update view
    response = client.post(
        reverse('person_update', kwargs={'pk': person.pk}), data)
    assert response.status_code == 302

    # Verify the person was updated
    person.refresh_from_db()
    assert person.name == 'Updated Alain'
    assert person.age == 23
    assert person.email == 'alainnambi@example.com'


@pytest.mark.django_db
def test_person_delete(client, person):
    # Access the person delete view
    response = client.post(reverse('person_delete', kwargs={'pk': person.pk}))
    assert response.status_code == 302

    # Check for deletion using pk
    assert not Person.objects.filter(pk=person.pk).exists()
