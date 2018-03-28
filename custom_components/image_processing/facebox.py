"""
Component that will perform facial recognition via a local machinebox instance.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.facebox
"""
import base64
from datetime import timedelta
import requests
import logging
import voluptuous as vol

from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.image_processing import (
    PLATFORM_SCHEMA, ImageProcessingEntity, CONF_SOURCE, CONF_ENTITY_ID,
    CONF_NAME)

_LOGGER = logging.getLogger(__name__)

CONF_URL = 'url'
CONF_CONCEPTS = 'concepts'
DEFAULT_CONCEPTS = 'NO_CONCEPT'

SCAN_INTERVAL = timedelta(seconds=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string,
    vol.Optional(CONF_CONCEPTS, default=[DEFAULT_CONCEPTS]):
        vol.All(cv.ensure_list, [cv.string]),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    entities = []
    for camera in config[CONF_SOURCE]:
        entities.append(Classifier(
            hass,
            camera.get(CONF_NAME),
            config[CONF_URL],
            config[CONF_CONCEPTS],
            camera[CONF_ENTITY_ID],
        ))
    add_devices(entities)


class Classifier(ImageProcessingEntity):
    """Perform a classification via a rest API."""

    ICON = 'mdi:file'

    def __init__(self, hass, name, url, concepts, camera_entity):
        """Init with the API key and model id"""
        self.hass = hass
        if name:  # Since name is optional.
            self._name = name
        else:
            self._name = "Classifier {0}".format(
                split_entity_id(camera_entity)[1])
        self._concepts = concepts
        self._camera_entity = camera_entity
        self._headers = {'content-type': 'application/json, charset=utf-8'}
        self._url = url
        self._classifications = {}  # The dict of classifications
        self._state = None    # The most likely classification

    def process_image(self, image):
        """Perform classification of a single image."""
        base64_img = base64.b64encode(image).decode('ascii')
        json_data = {"base64": base64_img}
        response = requests.post(
            self._url, headers=self._headers, json=json_data).json()

        if response['success']:
            data = response['tags']
            self._classifications = {item['tag']: round(
                100.0*item['confidence'], 1) for item in data}
            #_LOGGER.error("classifications %s", self._classifications)

            self._state = next(iter(self._classifications))
            self.fire_concept_events()
        else:
            self._state = "Request_failed"
            self._classifications = {}

    def fire_concept_events(self):
        """Fire an event for each concept identified."""
        identified_concepts = self._classifications.keys() & self._concepts
        for concept in identified_concepts:
            self.hass.bus.fire(
                'Classifier', {
                    CONF_ENTITY_ID: self._camera_entity,
                    'concept': concept,
                    })

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
        attr = self._classifications
        return attr

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.ICON

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
