"""The tests for the facebox component."""
from unittest.mock import patch

import pytest
import requests_mock

from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_IP_ADDRESS, CONF_PORT)
from homeassistant.setup import async_setup_component
import homeassistant.components.image_processing as ip

MOCK_IP = '192.168.0.1'
MOCK_PORT = '8080'

MOCK_JSON = {"facesCount": 1,
             "success": True,
             "faces": [{'confidence': 0.5812028911604818,
                        'id': 'john.jpg',
                        'matched': True,
                        'name': 'John Lennon',
                        'rect': {'height': 75,
                                 'left': 63,
                                 'top': 262,
                                 'width': 74}
                        }]
             }

VALID_ENTITY_ID = 'image_processing.facebox_demo_camera'
VALID_CONFIG = {
    ip.DOMAIN: {
        'platform': 'facebox',
        CONF_IP_ADDRESS: MOCK_IP,
        CONF_PORT: MOCK_PORT,
        ip.CONF_SOURCE: {
            ip.CONF_ENTITY_ID: 'camera.demo_camera'}
        },
    'camera': {
        'platform': 'demo'
        }
    }


@pytest.fixture
def mock_image():
    """Return a mock camera image."""
    with patch('homeassistant.components.camera.demo.DemoCamera.camera_image',
               return_value=b'Test') as image:
        yield image


async def test_setup_platform(hass):
    """Setup platform with one entity."""

    await async_setup_component(hass, ip.DOMAIN, VALID_CONFIG)
    assert hass.states.get(VALID_ENTITY_ID)


async def test_process_image(hass, mock_image):
    """Test processing of an image."""
    await async_setup_component(hass, ip.DOMAIN, VALID_CONFIG)
    assert hass.states.get(VALID_ENTITY_ID)

    with requests_mock.Mocker() as mock_req:
        url = "http://{}:{}/facebox/check".format(MOCK_IP, MOCK_PORT)
        mock_req.post(url, json=MOCK_JSON)
        data = {ATTR_ENTITY_ID: VALID_ENTITY_ID}
        await hass.services.async_call(ip.DOMAIN,
                                       ip.SERVICE_SCAN,
                                       service_data=data)
        await hass.async_block_till_done()

    state = hass.states.get(VALID_ENTITY_ID)
    assert state.state == '1'
    assert state.attributes.get('matched_faces') == {'John Lennon': 0.58}