from utpad_server import settings
from .models import Configuration, get_database_name


def site_configuration(request):
    configuration_dict = {}
    configuration_objects = Configuration.objects.all()
    for configuration_object in configuration_objects:
        configuration_dict["config_" + configuration_object.name] = configuration_object.value

    if not configuration_dict.get("config_site_name"):
        configuration_dict["config_site_name"] = get_database_name()
    if not configuration_dict.get("base_url"):
        configuration_dict["base_url"] = settings.FORCE_SCRIPT_NAME
    return configuration_dict
