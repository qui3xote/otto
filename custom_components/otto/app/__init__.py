import sys
import os
import pathlib
from .interpreter import Interpreter, Logger, Registrar

sys.path.append(hass.config.path("custom_components/otto/"))
from ottoparser import Auto, OttoContext, OttoBase


class OttoBuilder:
    def __init__(self, config):
        if not self.parse_config(config):
            log.error(f"INVALID CONFIG {config}")
            return

        logger = Logger(log_id="main", task="builder", debug_as_info=self.debug_as_info)

        registrar_log = Logger(
            log_id="main", task="registrar", debug_as_info=self.debug_as_info
        )
        registrar = Registrar(registrar_log)

        for f in self._files:
            stored_globals = {"area_groups": self.area_groups}

            logger.info(f"Reading {f}")
            try:
                file = task.executor(load_file, f)
                namespace = f.split("/")[-1:][0]
            except Exception as error:
                log.warning(f"Unable to read file: {f}")
                log.error(error)

            scripts = file.split(";")
            scripts = [s for s in scripts if len(s.strip()) > 0]

            for script in scripts:
                script_logger = Logger(
                    log_id=namespace, debug_as_info=self.debug_as_info
                )
                script_interpreter = Interpreter(script_logger)
                ctx = OttoContext(script_interpreter, script_logger)
                ctx.update_global_vars(stored_globals)
                OttoBase.set_context(ctx)

                try:
                    auto = Auto().parseString(script)[0]
                    auto.ctx.log.set_task(auto.controls.name)
                    logger.debug(f"Parsed {auto.controls.name}.")
                except Exception as error:
                    logger.error(f"FAILED TO PARSE: {script}\n{error}\n")

                try:
                    registrar.add(auto.controls, auto.triggers, auto.actions)
                    logger.debug(f"Registered {auto.controls.name}")
                except Exception as error:
                    logger.error(f"Register: {script}\n{error}\n")

                stored_globals = ctx.global_vars

    def parse_config(self, data):
        path = data.get("directory")
        if path is None:
            log.error("Script directory is required")
            return False
        else:
            try:
                self._files = task.executor(get_files, path)
            except Exception as error:
                log.error(f"Unable to read files from {path}. Error: {error}")
                return False

        self.area_groups = data.get("area_groups")
        if self.area_groups is None:
            self.area_groups = {}

        if data.get("verbose") == 1:
            self.debug_as_info = True
        else:
            self.debug_as_info = False

        return True


# Helpers


@pyscript_compile
def fileexists(path):
    return os.path.isfile(path)


@pyscript_compile
def get_files(path):
    files = []
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            if pathlib.Path(f).suffix == ".otto":
                files.append(os.path.join(path, f))
    return files


@pyscript_compile
def load_file(path):
    with open(path) as f:
        contents = f.read()

    return contents


@time_trigger("startup")
def startup():
    for app in pyscript.app_config:
        OttoBuilder(app)
