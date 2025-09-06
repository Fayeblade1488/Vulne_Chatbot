"""Basic tests for the vulnerable chatbot application"""

import pytest
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_import():
    """Test that app module can be imported"""
    try:
        from app import vulne_chat
        assert vulne_chat is not None
    except ImportError as e:
        pytest.fail(f"Failed to import app module: {e}")

def test_app_exists():
    """Test that Flask app exists"""
    from app.vulne_chat import app
    assert app is not None
    assert app.name == 'app.vulne_chat'

def test_routes_exist():
    """Test that main routes exist"""
    from app.vulne_chat import app
    
    # Get all registered routes
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    
    # Check for essential routes
    assert '/' in routes
    assert '/chat' in routes
    assert '/health' in routes
    assert '/api/models' in routes

def test_conversation_history_truncation():
    """Test that the conversation history is truncated to the latest 10 messages"""
    from app.vulne_chat import conversations, get_conversation_context

    conv_id = "test_session"
    conversations[conv_id] = []

    # Add 15 messages to the history
    for i in range(15):
        conversations[conv_id].append({"role": "user", "content": f"message {i}"})
        conversations[conv_id].append({"role": "assistant", "content": f"reply {i}"})

    # The history should now have 30 messages
    assert len(conversations[conv_id]) == 30

    # Trigger the context generation, which should truncate the history
    get_conversation_context(conv_id)

    # The history should now be truncated to 10 messages (user + assistant)
    assert len(conversations[conv_id]) == 10

def test_sql_injection_prevention():
    """Test that the /api/search endpoint is not vulnerable to SQL injection"""
    from app.vulne_chat import app, init_db

    init_db()

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        # This is a simple SQL injection payload
        malicious_query = "' OR '1'='1"

        response = client.get(f'/api/search?q={malicious_query}')

        # The request should be successful
        assert response.status_code == 200

        # The response should not contain any data, as the db is fresh
        assert len(response.get_json()['results']) == 0

def test_secrets_are_loaded_from_env():
    """Test that secrets are loaded from environment variables"""
    import os
    from app.vulne_chat import EMBEDDED_SECRETS

    # Set environment variables
    os.environ["ADMIN_TOKEN"] = "test_admin_token"
    os.environ["DB_PASSWORD"] = "test_db_password"
    os.environ["API_KEY"] = "test_api_key"
    os.environ["INTERNAL_SERVICE_KEY"] = "test_internal_service_key"
    os.environ["CANARY_TOKEN"] = "test_canary_token"

    # We need to reload the module to pick up the new environment variables
    import importlib
    from app import vulne_chat
    importlib.reload(vulne_chat)

    assert vulne_chat.EMBEDDED_SECRETS["admin_token"] == "test_admin_token"
    assert vulne_chat.EMBEDDED_SECRETS["db_password"] == "test_db_password"
    assert vulne_chat.EMBEDDED_SECRETS["api_key"] == "test_api_key"
    assert vulne_chat.EMBEDDED_SECRETS["internal_service_key"] == "test_internal_service_key"
    assert vulne_chat.EMBEDDED_SECRETS["canary_token"] == "test_canary_token"

def test_idor_prevention_on_profile():
    """Test that a user cannot view another user's profile"""
    from app.vulne_chat import app, init_db

    init_db()

    with app.test_client() as client:
        # Log in as user 2 (not an admin)
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'agent'

        # Attempt to access user 1's profile
        response = client.get('/profile?id=1')

        # The request should be denied
        assert response.status_code == 403

        # Log in as an admin
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'administrator'

        # Attempt to access user 2's profile
        response = client.get('/profile?id=2')

        # The request should be successful for an admin
        assert response.status_code == 200

def test_rce_endpoint_is_removed():
    """Test that the /run endpoint is removed"""
    from app.vulne_chat import app

    with app.test_client() as client:
        response = client.post('/run', json={'code': 'print("hello")'})
        assert response.status_code == 404

def test_xss_prevention_on_index():
    """Test that the index route is not vulnerable to XSS"""
    from app.vulne_chat import app

    with app.test_client() as client:
        malicious_script = "<script>alert('XSS')</script>"
        response = client.get(f'/?user={malicious_script}')

        assert response.status_code == 200

        # Check that the script is escaped
        assert b'&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;' in response.data
        assert b"<script>alert('XSS')</script>" not in response.data
