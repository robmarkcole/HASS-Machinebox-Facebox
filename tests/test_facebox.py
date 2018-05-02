"""The tests for the facebox component."""
from homeassistant.const import (CONF_IP_ADDRESS, CONF_PORT)
from homeassistant.setup import setup_component
import homeassistant.components.image_processing as ip

from tests.common import (
    get_test_home_assistant, assert_setup_component)

MOCK_IP = '192.168.0.1'
MOCK_PORT = '8080'

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


class TestFaceboxSetup(object):
    """Test class for image processing."""

    def setup_method(self):
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()

    def test_setup_platform(self):
        """Setup platform with one entity."""

        with assert_setup_component(1, ip.DOMAIN):
            setup_component(self.hass, ip.DOMAIN, VALID_CONFIG)

        assert self.hass.states.get(
            'image_processing.facebox_demo_camera')

    def teardown_method(self):
        """Stop everything that was started."""
        self.hass.stop()
