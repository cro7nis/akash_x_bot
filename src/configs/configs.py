from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="",
    settings_files=["configs/settings.yaml", "configs/.secrets.yaml"],
    environments=True,
    load_dotenv=True,
    merge_enabled=True,
    env_switcher="SWITCH_ENV",
)