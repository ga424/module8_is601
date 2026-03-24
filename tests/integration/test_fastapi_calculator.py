import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_api(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.parametrize(
    'route,payload,expected',
    [
        ('/add', {'a': 10, 'b': 5}, 15),
        ('/subtract', {'a': 10, 'b': 5}, 5),
        ('/multiply', {'a': 10, 'b': 5}, 50),
        ('/divide', {'a': 10, 'b': 2}, 5),
        ('/add', {'a': -2.5, 'b': 3.5}, 1.0),
        ('/divide', {'a': 7, 'b': 2}, 3.5),
    ],
)
def test_operation_routes_success(client, route, payload, expected):
    response = client.post(route, json=payload)
    assert response.status_code == 200
    assert response.json()['result'] == pytest.approx(expected)


def test_divide_by_zero_api(client):
    response = client.post('/divide', json={'a': 10, 'b': 0})
    assert response.status_code == 400
    assert 'error' in response.json()
    assert 'Cannot divide by zero!' in response.json()['error']


@pytest.mark.parametrize(
    'route,payload,expected_fragment',
    [
        ('/add', {'b': 1}, 'a'),
        ('/subtract', {'a': 1}, 'b'),
        ('/multiply', {'a': 'abc', 'b': 2}, 'a'),
        ('/divide', {'a': 2, 'b': None}, 'b'),
    ],
)
def test_operation_routes_validation_errors(client, route, payload, expected_fragment):
    response = client.post(route, json=payload)
    assert response.status_code == 400
    assert 'error' in response.json()
    assert expected_fragment in response.json()['error']


def test_operation_routes_malformed_json(client):
    response = client.post('/add', content='{"a": 1,', headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
    assert 'error' in response.json()


def test_divide_internal_error_returns_500(client, monkeypatch):
    def broken_divide(_a, _b):
        raise RuntimeError('boom')

    monkeypatch.setattr('main.divide', broken_divide)
    response = client.post('/divide', json={'a': 10, 'b': 2})
    assert response.status_code == 500
    assert response.json() == {'error': 'Internal Server Error'}
