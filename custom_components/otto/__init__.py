import os
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

import voluptuous as vol
from voluptuous.error import MultipleInvalid
from voluptuous.schema_builder import PREVENT_EXTRA

from .const import (
    DOMAIN,
    DOMAIN_DATA,
    SCRIPT_DIR,
    PYSCRIPT_FOLDER,
    PYSCRIPT_APP_FOLDER,
    PYSCRIPT_OTTO_FOLDER,
    OTTO_PYSCRIPT_FOLDER,
)

_LOGGER = logging.getLogger(__name__)

# config_schema = vol.Schema(
#     {
#         vol.Optional(SCRIPT_DIR, default='/config/ottoscripts/'): str
#     }
# )


def linkdir(target, name):
    os.symlink(target, name, target_is_directory=True)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OttoScript component."""

    # Check for pyscript folder
    pyscript_folder = hass.config.path(PYSCRIPT_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, pyscript_folder):
        _LOGGER.error(
            f"Pyscript Folder {pyscript_folder} not found. Install pyscript.")
        return False

    app_folder = hass.config.path(PYSCRIPT_APP_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, app_folder):
        _LOGGER.debug(f"Pyscript {app_folder} not found. Creating it.")
        await hass.async_add_executor_job(os.makedirs, app_folder)

    script_dir = hass.config.path(SCRIPT_DIR)
    if not await hass.async_add_executor_job(os.path.isdir, script_dir):
        _LOGGER.debug(f"Pyscript {script_dir} not found. Creating it.")
        await hass.async_add_executor_job(os.makedirs, script_dir)

    pyscript_otto_folder = hass.config.path(PYSCRIPT_OTTO_FOLDER)
    otto_pyscript_folder = hass.config.path(OTTO_PYSCRIPT_FOLDER)
    if not await hass.async_add_executor_job(
        os.path.islink,
        pyscript_otto_folder
    ):
        _LOGGER.debug(
            f"Pyscript App Folder {pyscript_otto_folder} not found. Linking."
        )
        await hass.async_add_executor_job(
            linkdir,
            otto_pyscript_folder,
            pyscript_otto_folder,
        )

    return True

    pyscript_config = hass.config.path(PYSCRIPT_FOLDER + "/config.yaml")
    if await hass.async_add_executor_job(os.path.isfile, pyscript_config):
        await hass.async_add_executor_job(os.utime, pyscript_config)
    else:
        _LOGGER.debug(
            f"Pyscript config not found at {pyscript_config}."
            "Manually reload pyscript to ensure proper libraries are loaded."
        )


async def async_setup_entry(hass, config_entry, async_add_devices):
    return


async def async_unload_entry(hass, entry):
    return
