import logging
import os
from pathlib import Path

import pandas as pd
import yaml
from django.contrib.auth.models import Group, User
from django.db import IntegrityError

from core.models import model_name_map as core_model_name_map
from core.serializers import serializer_map as api_serializer_map

model_name_map = {
    'auth': {'Group': Group, 'User': User},
    'core': core_model_name_map,
}

serializer_map = {}
serializer_map.update(api_serializer_map)

logger = logging.getLogger(__name__)


def save_data_to_folder(data_folder: str):
    os.makedirs(data_folder, exist_ok=True)
    for app_to_save in model_name_map.keys():
        logger.info(f"Going to write {app_to_save}")
        for model_to_save in model_name_map[app_to_save].keys():
            logger.info(f"Going to write f{model_to_save}")
            model_class = model_name_map[app_to_save][model_to_save]
            model_records = model_class.objects.all()
            os.makedirs(Path(data_folder, app_to_save), exist_ok=True)
            # for model_record in model_records:
            file_path = Path(data_folder, app_to_save, model_to_save + ".yaml")
            serializer_cls = serializer_map[model_class]
            if len(model_records) > 0:
                with open(str(file_path), 'w', ) as yaml_file:
                    yaml.dump_all(serializer_cls(model_records, many=True).data, yaml_file, sort_keys=False)


def load_data_from_folder(data_folder: str):
    if os.path.exists(data_folder):
        for app_to_save in model_name_map.keys():
            logger.info(f"Going to load {app_to_save}")
            if os.path.exists(Path(data_folder, app_to_save)):
                for model_to_save in model_name_map[app_to_save].keys():
                    logger.info(f"Going to load {model_to_save}")
                    model_class = model_name_map[app_to_save][model_to_save]
                    file_path = Path(data_folder, app_to_save, model_to_save + ".yaml")
                    if os.path.exists(file_path):
                        with open(str(file_path), 'r', ) as yaml_file:
                            model_records_data = yaml.safe_load_all(yaml_file)
                            for model_record_data in model_records_data:
                                m2m_fkeys = {}
                                foreign_keys = {}
                                for key in model_record_data.keys():
                                    field_cls = model_class.__dict__[key].__class__
                                    if 'ToMany' in field_cls.__name__:  # 'related_descriptors' in field_cls.__module__:
                                        m2m_fkeys[key] = model_record_data[key]
                                    if model_record_data[key] and (
                                            'ForwardOneToOne' in field_cls.__name__ or 'ForwardManyToOne' in field_cls.__name__):
                                        model_record_data[key] = model_class.__dict__[
                                            key].field.related_model.objects.get(id=model_record_data[key]['id'])

                                # for foreign_key in foreign_keys.keys():
                                #     del model_record_data[foreign_key]

                                for to_many_key in m2m_fkeys.keys():
                                    del model_record_data[to_many_key]

                                try:
                                    model_record = model_class.objects.create(**model_record_data)
                                    # TODO: Verify keys working well.
                                    logger.info(f"Created {str(model_record)}")
                                except IntegrityError as e:
                                    model_record = model_class.objects.get(id=model_record_data['id'])
                                    model_serializer_cls = serializer_map[model_class]
                                    logger.info(
                                        f"Ignoring existing data {model_record_data['id']} {str(e)}")

                                for to_many_key, value in m2m_fkeys.items():
                                    model_record.__getattribute__(to_many_key).set([int(item['id']) for item in value])


def save_data_to_excel(file_path: str):
    with pd.ExcelWriter(file_path) as writer:
        for app_to_save in model_name_map.keys():
            logger.info(f"Going to write {app_to_save}")
            for model_to_save in model_name_map[app_to_save].keys():
                logger.info(f"Going to write {model_to_save}")
                model_class = model_name_map[app_to_save][model_to_save]
                model_records = model_class.objects.all()
                serializer_cls = serializer_map[model_class]
                if len(model_records) > 0:
                    df = pd.DataFrame(serializer_cls(model_records, many=True).data)
                    df.to_excel(writer, sheet_name=app_to_save + "_" + model_to_save, index=False)
    logger.info(f"Wrote data to {file_path}")
