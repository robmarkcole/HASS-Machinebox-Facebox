# HASS-Machinebox-Facebox
Home-Assistant component for facial recognition with one-shot teaching using [facebox](https://machineboxio.com/docs/facebox/teaching-facebox). To teach facebox faces [use CURL or HTTP POST](https://machineboxio.com/docs/facebox/teaching-facebox#teach-paul-mccartney). Only taught faces are displayed in the entity state.

Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder).

Add to your Home-Assistant config:

```yaml
image_processing:
  - platform: facebox
    endpoint: localhost:8080
    confidence: 0.5
    scan_interval: 5
    source:
      - entity_id: camera.local_file
```
Configuration variables:
- **endpoint**: the ip (here `localhost`) and port (default `8080`) of your facebox instance
- **confidence**: The confidence on a scale of 0-1 of a taught face (default `0` for unrecognised faces).
- **scan_interval** (optional): [see the docs](https://www.home-assistant.io/docs/configuration/platform_options/#scan-interval), units seconds, default of 10 seconds.
- **source**: Must be a camera.

The component adds an `image_processing` entity. The state of the entity is the name of any taught faces that are found in the image. If no taught faces are found the state of the entity is `unknown`. The entity has an attribute `total_faces` which is the total number of faces found. The attribute `faces` contains a list of bounding boxes for the faces.

#### Limiting computation
[Image-classifier components](https://www.home-assistant.io/components/image_processing/) process the image from a camera at a fixed period given by the `scan_interval`. This leads to excessive computation if the image on the camera hasn't changed (for example if you are using a [local file camera](https://www.home-assistant.io/components/camera.local_file/) to display an image captured by a motion triggered system and this doesn't change often). The default `scan_interval` [is 10 seconds](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L27). You can override this by adding to your config `scan_interval: 10000` (setting the interval to 10,000 seconds), and then call the `scan` [service](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L62) when you actually want to process a camera image. So in my setup, I use an automation to call `scan` when a new motion triggered image has been saved and displayed on my local file camera.

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Facebox/blob/master/usage.png" width="500">
</p>

#### Intended Usage
I will use facial recognition for user authentication, and this will allow them to disarm their [alarm system]( https://www.hackster.io/colinodell/diy-alarm-control-panel-for-home-assistant-ac1813). I will show how facial recognition alone is not secure (spoofing with a photo), then add [bluetooth presence detection](https://www.hackster.io/vpetersson/sonar-wireless-foot-traffic-information-for-retail-b17cc1) and/or other [presence detection](https://www.home-assistant.io/components/#presence-detection) and use stats to show the improvement in security.
