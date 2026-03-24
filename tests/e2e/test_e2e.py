import pytest


@pytest.mark.e2e
def test_hello_world(page, fastapi_server):
    page.goto('http://localhost:8000')
    assert page.inner_text('h1') == 'Hello World'


@pytest.mark.e2e
def test_calculator_add(page, fastapi_server):
    page.goto('http://localhost:8000')
    page.fill('#a', '10')
    page.fill('#b', '5')
    page.click('button:text("Add")')
    page.wait_for_function("() => document.querySelector('#result').innerText.length > 0")
    assert page.inner_text('#result') in ('Calculation Result: 15', 'Calculation Result: 15.0')


@pytest.mark.e2e
def test_calculator_divide_by_zero(page, fastapi_server):
    page.goto('http://localhost:8000')
    page.fill('#a', '10')
    page.fill('#b', '0')
    page.click('button:text("Divide")')
    page.wait_for_function("() => document.querySelector('#result').innerText.length > 0")
    assert page.inner_text('#result') == 'Error: Cannot divide by zero!'
