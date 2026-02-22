import pytest
from app import app, db
from models import Contact


# ============================
# FIXTURES
# ============================

@pytest.fixture
def client():
    """Create a test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_contact():
    """Create a sample contact"""
    contact = Contact(
        name='John Doe',
        phone='1234567890',
        email='john@example.com',
        type='Personal'
    )
    db.session.add(contact)
    db.session.commit()
    return contact


# ============================
# WEB ROUTE TESTS
# ============================

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_add_contact(client):
    data = {
        'name': 'Jane Doe',
        'phone': '9876543210',
        'email': 'jane@example.com',
        'type': 'Personal'
    }

    response = client.post('/add', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert b'Jane Doe' in response.data


def test_update_contact(client, sample_contact):
    data = {
        'name': 'John Smith',
        'phone': sample_contact.phone,
        'email': sample_contact.email,
        'type': sample_contact.type,
        'submit': 'Submit'
    }

    response = client.post(
        f'/update/{sample_contact.id}',
        data=data,
        follow_redirects=True
    )

    assert response.status_code == 200

    updated = db.session.get(Contact, sample_contact.id)
    assert updated.name == 'John Smith'


# ============================
# API TESTS
# ============================

def test_get_contacts_api(client, sample_contact):
    response = client.get('/api/contacts')

    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'John Doe'


def test_create_contact_api(client):
    data = {
        'name': 'API User',
        'phone': '5555555555',
        'email': 'api@example.com',
        'type': 'Work'
    }

    response = client.post('/api/contacts', json=data)

    assert response.status_code == 201
    assert response.get_json()['name'] == 'API User'


def test_get_nonexistent_contact(client):
    response = client.get('/api/contacts/999')

    assert response.status_code == 404