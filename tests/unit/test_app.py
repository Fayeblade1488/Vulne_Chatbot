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
