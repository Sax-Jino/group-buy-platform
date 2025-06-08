import pytest
from unittest.mock import patch, MagicMock
from services.logistics_service import LogisticsService

@pytest.fixture
def mock_app_config(monkeypatch):
    class MockApp:
        config = {'AFTERSHIP_API_KEY': 'fake-key'}
    monkeypatch.setattr('services.logistics_service.current_app', MockApp())

@patch('services.logistics_service.tracking')
def test_track_shipment_success(mock_tracking, mock_app_config):
    # Arrange
    mock_client = MagicMock()
    mock_tracking.Client.return_value = mock_client
    mock_tracking.Configuration.return_value = MagicMock()
    mock_client.get_tracking.return_value = {'tag': 'InTransit', 'checkpoints': []}
    service = LogisticsService()
    service.api = mock_client

    # Act
    result = service.track_shipment('123456789', 'taiwan-post')

    # Assert
    assert result['tag'] == 'InTransit'
    mock_client.get_tracking.assert_called_once_with(tracking_number='123456789', slug='taiwan-post')

@patch('services.logistics_service.tracking')
def test_track_shipment_no_courier_detected(mock_tracking, mock_app_config):
    mock_client = MagicMock()
    mock_tracking.Client.return_value = mock_client
    mock_tracking.Configuration.return_value = MagicMock()
    mock_client.detect.return_value = {'couriers': [{'slug': 'taiwan-post'}]}
    mock_client.get_tracking.return_value = {'tag': 'InTransit', 'checkpoints': []}
    service = LogisticsService()
    service.api = mock_client

    result = service.track_shipment('123456789')
    assert result['tag'] == 'InTransit'
    mock_client.detect.assert_called_once_with('123456789')
    mock_client.get_tracking.assert_called_once_with(tracking_number='123456789', slug='taiwan-post')

@patch('services.logistics_service.tracking')
def test_track_shipment_fail(mock_tracking, mock_app_config):
    mock_client = MagicMock()
    mock_tracking.Client.return_value = mock_client
    mock_tracking.Configuration.return_value = MagicMock()
    mock_client.get_tracking.side_effect = Exception('API error')
    service = LogisticsService()
    service.api = mock_client

    result = service.track_shipment('123456789', 'taiwan-post')
    assert result is None
