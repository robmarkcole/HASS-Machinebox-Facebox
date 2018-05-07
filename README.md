# HASS-Machinebox-Facebox
Home-Assistant component for face detection (number of faces) and identification (recognising trained faces) using [facebox](https://machineboxio.com/docs/facebox/teaching-facebox).

Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder).

Add to your Home-Assistant config:

```yaml
image_processing:
  - platform: facebox_face_detect
    ip_address: localhost # or e.g. 192.168.0.1
    port: 8080
    source:
      - entity_id: camera.local_file
```
Configuration variables:
- **ip_address**: the ip address of your facebox instance.
- **port**: the port of your facebox instance.
- **source**: Must be a camera.

The component adds an `image_processing` entity where the state of the entity is the number of faces that are found in the camera image. The attribute `response_time` is the time in seconds for facebox to perform processing on an image. Your `scan_interval` must be longer than `response_time`. Note that the bounding boxes of faces are also accessible from the attributes. TO DO - write a CC for adding bounding boxes to the image.

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
[Image-classifier components](https://www.home-assistant.io/components/image_processing/) process the image from a camera at a fixed period given by the `scan_interval`. This leads to excessive computation if the image on the camera hasn't changed (for example if you are using a [local file camera](https://www.home-assistant.io/components/camera.local_file/) to display an image captured by a motion triggered system and this doesn't change often). The default `scan_interval` [is 10 seconds](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L27). You can override this by adding to your config `scan_interval: 10000` (setting the interval to 10,000 seconds), and then call the `scan` [service](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L62) when you actually want to process a camera image. So in my setup, I use an automation to call `scan` when a new image is available.

You can also reduce the time for face detection (counting number of faces only) by setting the environment variable `-e MB_FACEBOX_DISABLE_RECOGNITION=true` when you `run` Docker. Note that the `teach` endpoint is not available when you do this, and all recognition is disabled. However detection time is reduced by 50-75%.
