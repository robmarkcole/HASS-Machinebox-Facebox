# HASS-Machinebox-Facebox

Home-Assistant component for face detection (number of faces) and identification (recognising trained faces) using [facebox](https://machineboxio.com/docs/facebox/teaching-facebox). The stable version of the component is added to Home-Assistant, and this repo should be considered development.

Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder).

Add to your Home-Assistant config:

```yaml
image_processing:
  - platform: facebox
    ip_address: localhost # or e.g. 192.168.0.1
    port: 8080
    username: my_username
    password: my_password
    source:
      - entity_id: camera.local_file
```
Configuration variables:
- **ip_address**: the ip address of your facebox instance.
- **port**: the port of your facebox instance.
- **username**: (Optional) the username if you are using authentication.
- **password**: (Optional) the password if you are using authentication
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

## Teach service
The service `image_processing.facebox_teach_face` can be used to teach Facebox faces, as described in [this blog post](https://towardsdatascience.com/every-superheros-secret-identity-wouldn-t-fool-modern-face-recognition-32c6fda07bb9). Call the service from the `dev-service` panel. Valid image filetypes are those ending in `.jpg`, `.png`, `.jpeg`. Example valid service data is:
```yaml
{
  "entity_id": "image_processing.facebox_local_file",
  "name": "superman",
  "file_path": "/Users/robincole/.homeassistant/images/superman_1.jpeg"
}
```

You can use an automation to receive a notification when you train a face:
```yaml
- id: '1533703568569'
  alias: Face taught
  trigger:
  - event_data:
      service: facebox_teach_face
    event_type: call_service
    platform: event
  condition: []
  action:
  - service: notify.pushbullet
    data_template:
      message: '{{ trigger.event.data.service_data.name }} taught 
      with file {{ trigger.event.data.service_data.file_path }}'
      title: Face taught notification
```

Any errors on teaching will be reported in the logs. If you enable [system_log](https://www.home-assistant.io/components/system_log/) events:
```yaml
system_log:
  fire_event: true
```

you can create an automation to receive notifications on Facebox errors:
```yaml
- id: '1533703568577'
  alias: Facebox error
  trigger:
    platform: event
    event_type: system_log_event
  condition:
    condition: template
    value_template: '{{ "facebox" in trigger.event.data.message }}'
  action:
  - service: notify.pushbullet
    data_template:
      message: '{{ trigger.event.data.message }}'
      title: Facebox error
```

## Appearence on HA front-end

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Facebox/blob/master/usage.png" width="750">
</p>

#### Run Machinebox
Run facebox with:
```
MB_KEY="INSERT-YOUR-KEY-HERE"

sudo docker run -p 8080:8080 -e "MB_KEY=$MB_KEY" machinebox/facebox
```

To run [with authentication](https://machinebox.io/docs/machine-box-apis#basic-authentication):
```
sudo docker run -e "MB_BASICAUTH_USER=my_username" -e "MB_BASICAUTH_PASS=my_password" -p 8080:8080 -e "MB_KEY=$MB_KEY" machinebox/facebox
```

If you receive errors complaining of lack of RAM, but you do have sufficient ram, try the `machinebox/facebox_noavx` container.

#### Optimising resources
[Image processing components](https://www.home-assistant.io/components/image_processing/) process the image from a camera at a fixed period given by the `scan_interval`. This leads to excessive computation if the image on the camera hasn't changed (for example if you are using a [local file camera](https://www.home-assistant.io/components/camera.local_file/) to display an image captured by a motion triggered system and this doesn't change often). The default `scan_interval` [is 10 seconds](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L27). You can override this by adding to your config `scan_interval: 10000` (setting the interval to 10,000 seconds), and then call the `scan` [service](https://github.com/home-assistant/home-assistant/blob/98e4d514a5130b747112cc0788fc2ef1d8e687c9/homeassistant/components/image_processing/__init__.py#L62) when you actually want to process a camera image. So in my setup, I use an automation to call `scan` when a new image is available.

You can also reduce the time for face detection (counting number of faces only) by setting the environment variable `-e MB_FACEBOX_DISABLE_RECOGNITION=true` when you `run` Docker. As the variable name states, this disables facial recognition and in my experience detection time is reduced by 50-75%. Note that the `teach` endpoint is not available when you disable recognition.

#### Training
You can use [this script](https://github.com/robmarkcole/facebox_python) to train facebox. Note that training is only possible when facebox is in recognition mode (i.e. default behaviour of `MB_FACEBOX_DISABLE_RECOGNITION=false`).
