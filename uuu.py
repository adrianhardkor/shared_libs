#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import re
import soap
import deepdiff
import yaml
data = '''{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 41,
      "url": "https://netbox.cmh.wowcloud.biz/api/dcim/devices/41/",
      "name": "test_akrygowski",
      "display_name": "test_akrygowski",
      "device_type": {
        "id": 20,
        "url": "https://netbox.cmh.wowcloud.biz/api/dcim/device-types/20/",
        "manufacturer": {
          "id": 1,
          "url": "https://netbox.cmh.wowcloud.biz/api/dcim/manufacturers/1/",
          "name": "Cisco",
          "slug": "cisco"
        },
        "model": "Test",
        "slug": "test",
        "display_name": "Cisco Test"
      },
      "device_role": {
        "id": 1,
        "url": "https://netbox.cmh.wowcloud.biz/api/dcim/device-roles/1/",
        "name": "Router",
        "slug": "router"
      },
      "tenant": {
        "id": 73,
        "url": "https://netbox.cmh.wowcloud.biz/api/tenancy/tenants/73/",
        "name": "ARC Lab",
        "slug": "arc-lab"
      },
      "platform": null,
      "serial": "",
      "asset_tag": null,
      "site": {
        "id": 1,
        "url": "https://netbox.cmh.wowcloud.biz/api/dcim/sites/1/",
        "name": "CMH WOW Datacenter",
        "slug": "cmh-wow-datacenter"
      },
      "rack": null,
      "position": null,
      "face": null,
      "parent_device": null,
      "status": {
        "value": "active",
        "label": "Active"
      },
      "primary_ip": null,
      "primary_ip4": null,
      "primary_ip6": null,
      "cluster": null,
      "virtual_chassis": null,
      "vc_position": null,
      "vc_priority": null,
      "comments": "",
      "local_context_data": null,
      "tags": [],
      "custom_fields": {},
      "config_context": {},
      "created": "2021-04-05",
      "last_updated": "2021-04-05T19:13:48.524811Z"
    }
  ]
}'''

data = json.loads(data)
print(yaml.dump(data['results']))

