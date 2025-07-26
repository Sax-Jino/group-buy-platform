import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pytest
from unittest.mock import patch, MagicMock
from backend.services.logistics_service import LogisticsService
from backend.app import create_app
from backend.config import TestingConfig

@pytest.fixture
def mock_app_config(monkeypatch):
    class MockApp:
        config = {'AFTERSHIP_API_KEY': 'fake-key'}
    monkeypatch.setattr('backend.services.logistics_service.current_app', MockApp())

@pytest.fixture(scope='module', autouse=True)
def app_context():
    app = create_app(TestingConfig)
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()

@patch('backend.services.logistics_service.APIv4')
def test_track_shipment_success(MockAPIv4, mock_app_config):
    # Arrange
    mock_api = MagicMock()
    MockAPIv4.return_value = mock_api
    mock_tracking_obj = MagicMock()
    mock_tracking_obj.tracking = {'tag': 'InTransit', 'checkpoints': []}
    mock_api.trackings.get.return_value = mock_tracking_obj
    service = LogisticsService(api_key='fake-key')

    # Act
    result = service.track_shipment('123456789', 'taiwan-post')

    # Assert
    assert result['tag'] == 'InTransit'
    mock_api.trackings.get.assert_called_once_with('123456789', 'taiwan-post')

@patch('backend.services.logistics_service.APIv4')
def test_track_shipment_no_courier_detected(MockAPIv4, mock_app_config):
    mock_api = MagicMock()
    MockAPIv4.return_value = mock_api
    mock_api.couriers.detect.return_value = None
    service = LogisticsService(api_key='fake-key')

    # Act
    result = service.track_shipment('123456789', None)
    # Assert
    assert result is None

@patch('backend.services.logistics_service.APIv4')
def test_track_shipment_fail(MockAPIv4, mock_app_config):
    mock_api = MagicMock()
    MockAPIv4.return_value = mock_api
    mock_api.trackings.get.side_effect = Exception('API error')
    service = LogisticsService(api_key='fake-key')

    result = service.track_shipment('123456789', 'taiwan-post')
    assert result is None
