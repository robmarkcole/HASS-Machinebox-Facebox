# HASS-Machinebox-Facebox

Home-Assistant component for face detection (number of faces) and identification (recognising trained faces) using [facebox](https://machineboxio.com/docs/facebox/teaching-facebox). The stable version of the component is added to Home-Assistant, and this repo should be considered development.

Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder).

Add to your Home-Assistant config:

```yaml
image_processing:
  - platform: facebox
    ip_address: localhost # or e.g. 192.168.0.1
    port: 8080
    source:
      - entity_id: camera.local_file
```
Configuration variables:
- **ip_address**: the ip address of your facebox instance.
- **port**: the port of your facebox instance.
- **source**: Must be a camera.


The component adds an `image_processing` entity where the state of the entity is the total number of faces that are found in the camera image. The name and confidence of matched faces are in the `matched_faces` attribute, whilst the `faces` attribute additionally lists the matching `image_id` and `bounding_box` of matched faces. An `image_processing.detect_face` event is fired for every matched face.

## Automations
Use the events fired to trigger automations. The following example automation fires a notification with a local_file camera image when Ringo Star is recognised:

```yaml
- id: '12345'
  alias: Ringo Starr recognised
  trigger:
    platform: event
    event_type: image_processing.detect_face
    event_data:
      name: 'Ringo_Starr'
  action:
    service: notify.platform
    data_template:
      message: Ringo_Starr recognised with probability {{ trigger.event.data.confidence }}
      title: Door-cam notification
```

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Facebox/blob/master/usage.png" width="750">
</p>

#### Run Machinebox
Run facebox with:
```
MB_KEY="INSERT-YOUR-KEY-HERE"

sudo docker run -p 8080:8080 -e "MB_KEY=$MB_KEY" machinebox/facebox
```

#### Optimising resources
[Image processing components](https://www.home-assistant.io/components/image_processing/) process the image from a camera at a fixed period given by the `scan_interval`. This leads to excessive computation if the image on the camera hasn't changed (for example if you are using a [local file camera](https://www.home-assistant.io/components/camera.local_file/) to display an image captured by a motion triggered system and this doesn't change often). The default `scan_interval` [is 10 seconds](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L27). You can override this by adding to your config `scan_interval: 10000` (setting the interval to 10,000 seconds), and then call the `scan` [service](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L62) when you actually want to process a camera image. So in my setup, I use an automation to call `scan` when a new image is available.

You can also reduce the time for face detection (counting number of faces only) by setting the environment variable `-e MB_FACEBOX_DISABLE_RECOGNITION=true` when you `run` Docker. As the variable name states, this disables facial recognition and in my experience detection time is reduced by 50-75%. Note that the `teach` endpoint is not available when you disable recognition.

#### Training
You can use [this script](https://github.com/robmarkcole/facebox_python) to train facebox. Note that training is only possible when facebox is in recognition mode (i.e. default behaviour of `MB_FACEBOX_DISABLE_RECOGNITION=false`).
