"""
Component that will perform facial recognition via a local machinebox instance.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.facebox
"""
import base64
from datetime import timedelta
import io
import requests
import logging
import voluptuous as vol

from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE, CONF_ENTITY_ID,
    CONF_NAME)

_LOGGER = logging.getLogger(__name__)

CONF_ENDPOINT = 'endpoint'

SCAN_INTERVAL = timedelta(seconds=8)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENDPOINT): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(Facebox(
            hass,
            camera.get(CONF_NAME),
            config[CONF_ENDPOINT],
            camera[CONF_ENTITY_ID],
        ))
    add_devices(entities)


class Facebox(ImageProcessingEntity):
    """Perform a classification via a Facebox."""

    ICON = 'mdi:file'

    def __init__(self, hass, name, endpoint, camera_entity):
        """Init with the API key and model id"""
        self.hass = hass
        if name:  # Since name is optional.
            self._name = name
        else:
            self._name = "Facebox {0}".format(
                split_entity_id(camera_entity)[1])
        self._camera_entity = camera_entity
    #    self._headers = {'content-type': 'application/json, charset=utf-8'}
        self._url = "http://{}/facebox/check".format(endpoint)
        self._state = None

    def process_image(self, image):
        """Process an image."""
        response = requests.post(
            self._url,
            json=self.encode_image(image)
            ).json()

        if response['success']:
            self._state = response['facesCount']
        else:
            self._state = "Request_failed"

    def encode_image(self, image):
        """base64 encode an image stream."""
        base64_img = base64.b64encode(image).decode('ascii')
        return {"base64": base64_img}

    def save_image(self, image):
        """Save an image stream and return the filename."""
        from PIL import Image
        stream = io.BytesIO(image)
        img = Image.open(stream)
        IMG = 'facebox.jpg'
        img.save(IMG)
        return IMG

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return 'class'

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera_entity

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        return attr

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.ICON

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
