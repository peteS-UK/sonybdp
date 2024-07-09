from __future__ import annotations

import logging

from .const import DOMAIN

import voluptuous as vol

from homeassistant.components.media_player import (
    PLATFORM_SCHEMA,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)

from homeassistant import config_entries, core

from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    config_validation as cv,
    discovery_flow,
    entity_platform,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.start import async_at_start

_LOGGER = logging.getLogger(__name__)


from .const import (
    SERVICE_SEND_COMMAND,
    DEFAULT_NAME,
    CONF_BROADLINK_NAME,
    CONF_IR_ENTITY,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=None): cv.string,
    }
)

SUPPORT_MP = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:

    config = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            BDPDevice(
                hass,
                config[CONF_NAME],
                config[CONF_IR_ENTITY],
                config[CONF_BROADLINK_NAME],
            )
        ]
    )


class BDPDevice(MediaPlayerEntity):
    # Representation of a Emotiva Processor

    def __init__(self, hass, name, ir_entity_id, broadlink_name):

        self._hass = hass
        self._state = MediaPlayerState.OFF
        self._entity_id = "media_player.sonybdp"
        self._unique_id = "sonybdp_" + name.replace(" ", "_").replace("-", "_").replace(
            ":", "_"
        )
        self._device_class = "receiver"
        self._name = name
        self._ir_entity_id = ir_entity_id
        self._broadlink_name = broadlink_name

    should_poll = False

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return "mdi:disc"

    @property
    def state(self) -> MediaPlayerState:
        return self._state

    @property
    def name(self):
        # return self._device.name
        return None

    @property
    def has_entity_name(self):
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._unique_id)
            },
            name=self._name,
            manufacturer="Sony",
            model="BDP",
        )

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def device_class(self):
        return self._device_class

    @entity_id.setter
    def entity_id(self, entity_id):
        self._entity_id = entity_id

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        return SUPPORT_MP

    async def _send_broadlink_command(self, command):

        await self._hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._ir_entity_id,
                "num_repeats": "1",
                "delay_secs": "0.4",
                "device": self._broadlink_name,
                "command": command,
            },
        )

    async def async_turn_off(self) -> None:
        await self._send_broadlink_command("power")
        self._state = MediaPlayerState.OFF
        self.async_schedule_update_ha_state()

    async def async_turn_on(self) -> None:
        await self._send_broadlink_command("power")
        self._state = MediaPlayerState.ON
        self.async_schedule_update_ha_state()

    async def async_media_stop(self) -> None:
        """Send stop command to media player."""
        await self._send_broadlink_command("stop")
        self._state = MediaPlayerState.IDLE
        self.async_schedule_update_ha_state()

    async def async_media_play(self) -> None:
        """Send play command to media player."""
        await self._send_broadlink_command("play")
        self._state = MediaPlayerState.PLAYING
        self.async_schedule_update_ha_state()

    async def async_media_pause(self) -> None:
        """Send pause command to media player."""
        await self._send_broadlink_command("pause")
        self._state = MediaPlayerState.PAUSED
        self.async_schedule_update_ha_state()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self._send_broadlink_command("next")

    async def async_media_previous_track(self) -> None:
        """Send prev track command."""
        await self._send_broadlink_command("previous")

    async def async_update(self):
        pass
