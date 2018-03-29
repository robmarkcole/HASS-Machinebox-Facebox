"""
Component that will perform facial recognition via a local machinebox instance.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.facebox
"""
import base64
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
SAVE_BOUNDING = True
IMAGES_FOLDER = "/Users/robincole/.homeassistant/images/"

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
        self._url = "http://{}/facebox/check".format(endpoint)
        self._state = None
        self._attr = {}

    def process_image(self, image):
        """Process an image."""
        response = requests.post(
            self._url,
            json=self.encode_image(image)
            ).json()

        if response['success']:
            self._state, self._attr, boxes = self.process_response(response)
            if SAVE_BOUNDING:
                self.save_boxes_image(self.save_image(image), boxes)
        else:
            self._state = "Request_failed"
            self._attr = {}

    def process_response(self, response):
        """Return the number of faces and identified faces."""
        total_faces = response['facesCount']
        attr = {}
        bounding_boxes = []
        for face in response['faces']:
            bounding_boxes.append(face['rect'])
            if face['matched']:
                attr[face['name']] = round(face['confidence'], 2)
        return total_faces, attr, bounding_boxes

    def encode_image(self, image):
        """base64 encode an image stream."""
        base64_img = base64.b64encode(image).decode('ascii')
        return {"base64": base64_img}

    def save_image(self, image):
        """Save an image stream and return the filename."""
        from PIL import Image
        stream = io.BytesIO(image)
        img = Image.open(stream)
        IMG = IMAGES_FOLDER + 'facebox.jpg'
        img.save(IMG)
        return IMG

    def save_boxes_image(self, img_file, bounding_boxes):
        """Take an image file and dict of bounding boxes and save the
        boxes on a copy of the image."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        img = plt.imread(img_file)
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(img)
        for box in bounding_boxes:
            x = box['left']
            y = box['top']
            width = box['width']
            height = box['height']

            rect = patches.Rectangle(
                (x, y), width, height,
                linewidth=5, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
        plt.savefig(IMAGES_FOLDER + "boxed_image.png")

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
        return self._attr

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self.ICON

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
