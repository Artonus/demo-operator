#!/usr/bin/env python3
# Copyright 2021 Bartosz Bratuś
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging

from ops.charm import CharmBase, ConfigChangedEvent, PebbleReadyEvent
from ops.main import main
from ops.model import ActiveStatus, WaitingStatus

logger = logging.getLogger(__name__)


class DemoOperatorCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_config_changed(self, event: ConfigChangedEvent):
        """Handle the config-changed event"""
        logger.warning("Entered the config changed action")
        # Get the minecraft container so we can configure/manipulate it
        container = self.unit.get_container("minecraft")
        # Create a new config layer
        layer = self._pebble_layer()

        if container.can_connect():
            # Get the current config
            services = container.get_plan().to_dict().get("services", {})
            # Check if there are any changes to services
            if services != layer["services"]:
                # Changes were made, add the new layer
                container.add_layer("minecraft", layer, combine=True)
                logging.info("Added updated layer 'minecraft' to Pebble plan")
                # Restart it and report a new status to Juju
                container.restart("minecraft")
                logging.info("Restarted minecraft service")
            # All is well, set an ActiveStatus
            self.unit.status = ActiveStatus()
        else:
            self.unit.status = WaitingStatus("waiting for Pebble in workload container")

    def _pebble_layer(self):
        """Returns pebble configuration for the minecraft layer"""
        return {
            "summary": "minecraft layer",
            "description": "pebble config layer for minecraft",
            "services": {
                "minecraft": {
                    "override": "replace",
                    "summary": "minecraft",
                    "command": self._pebble_layer_command,
                    "startup": "enabled",
                    "environment": {
                        "EULA": "TRUE"
                    }
                }
            },
        }

    @property
    def _pebble_layer_command(self):
        """Returns the command needed to run the minecraft continer"""
        return "/start"

if __name__ == "__main__":
    main(DemoOperatorCharm)
