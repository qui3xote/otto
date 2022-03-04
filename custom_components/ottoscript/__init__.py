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
    PYSCRIPT_OTTO_APP_FOLDER,
    OTTO_PYSCRIPT_FOLDER
)

_LOGGER = logging.getLogger(__name__)

config_schema = vol.Schema(
    {
        vol.Optional(CONFIG_SCRIPT_DIR, default='/config/ottoscripts/'): str
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the OttoScript component."""
    # @TODO: Add setup code.
    # Check for pyscript install - stop if not installed
    # Read in configuration - script directory.
    # Check if app is installed - if not, copy files.
    # ^will need to check version installed. Or just reinstall
    # every time.
    # if pyscript running - reload.
    # If pyscript not running... wait? Or just stop?
    # Add script dir to watchdog. (borrow code form pyscript)
    # if any otto files change, trigger pyscript reload.

    # Check for pyscript folder
    pyscript_folder = hass.config.path(PYSCRIPT_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, pyscript_folder):
        _LOGGER.error(
            f"Pyscript Folder {pyscript_folder} not found. Install pyscript.")
        return False

    app_folder = hass.config.path(PYSCRIPT_APP_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, app_folder):
        _LOGGER.debug(
            f"Pyscript {app_folder} not found. Creating it.")
        await hass.async_add_executor_job(os.makedirs, app_folder)

    script_dir = hass.config.path(SCRIPT_DIR)
    if not await hass.async_add_executor_job(os.path.isdir, script_dir):
        _LOGGER.debug(
            f"Pyscript {script_dir} not found. Creating it.")
        await hass.async_add_executor_job(os.makedirs, script_dir)

    pyscript_otto_app_folder = hass.config.path(PYSCRIPT_OTTO_APP_FOLDER)
    if not await hass.async_add_executor_job(os.path.isdir, pyscript_otto_app_folder):
        _LOGGER.debug(
            f"Pyscript App Folder {pyscript_otto_app_folder} not found. Linking.")
        await hass.async_add_executor_job(os.symlink, pyscript_otto_app_folder, OTTO_PYSCRIPT_FOLDER)

    return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    return


async def async_unload_entry(hass, entry):
    return
