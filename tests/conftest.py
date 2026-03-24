import subprocess
import sys
import time

import pytest
import requests
from playwright.sync_api import sync_playwright


@pytest.fixture(scope='session')
def fastapi_server():
    """Start FastAPI for E2E tests and stop it at session end."""
    fastapi_process = subprocess.Popen([sys.executable, 'main.py'])

    server_url = 'http://127.0.0.1:8000/'
    timeout = 30
    start_time = time.time()
    server_up = False

    while time.time() - start_time < timeout:
        try:
            response = requests.get(server_url, timeout=2)
            if response.status_code == 200:
                server_up = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)

    if not server_up:
        fastapi_process.terminate()
        raise RuntimeError('FastAPI server failed to start within timeout period.')

    yield

    fastapi_process.terminate()
    fastapi_process.wait()


@pytest.fixture(scope='session')
def playwright_instance_fixture():
    with sync_playwright() as playwright_instance:
        yield playwright_instance


@pytest.fixture(scope='session')
def browser(playwright_instance_fixture):
    browser_instance = playwright_instance_fixture.chromium.launch(headless=True)
    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope='function')
def page(browser):
    browser_page = browser.new_page()
    yield browser_page
    browser_page.close()
