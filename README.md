# HASS-Machinebox-Facebox
Home-Assistant component for facial recognition with one-shot teaching using Machinebox.io https://machineboxio.com/docs/facebox/teaching-facebox
Place the custom_components folder in your configuration directory (or add its contents to an existing custom_components folder).
Add to your HA config:

```yaml
image_processing:
  - platform: facebox
    endpoint: localhost:8080
    confidence: 0.5
    source:
      - entity_id: camera.local_file
```

**endpoint**: the ip and port of your facebox instance
**confidence**: The confidence on a scale of 0-1 of a matched face. Only faces that have been [taught](https://machineboxio.com/docs/facebox/teaching-facebox#teach-paul-mccartney) to facebox can be matched.
**source**: Must be a camera.

<p align="center">
<img src="https://github.com/robmarkcole/HASS-Machinebox-Facebox/blob/master/usage.png" width="500">
</p>

## Plan
Overall plan for this component: I aim to tackle the problem of user authentication in Home-Assistant. I will use facial recognition/classification to determine when a user is identified, and this will allow them to disarm their [alarm system]( https://www.hackster.io/colinodell/diy-alarm-control-panel-for-home-assistant-ac1813). I will show how facial recognition alone is not secure (spoofing with a photo), then add [bluetooth presence detection](https://www.hackster.io/vpetersson/sonar-wireless-foot-traffic-information-for-retail-b17cc1) and/or other [presence detection](https://www.home-assistant.io/components/#presence-detection) and use stats to show the improvement in security.
