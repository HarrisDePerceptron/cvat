# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from tempfile import TemporaryDirectory

from datumaro.components.project import Dataset
from cvat.apps.dataset_manager.bindings import CvatTaskDataExtractor, \
    import_dm_annotations
from cvat.apps.dataset_manager.util import make_zip_archive

from .registry import dm_env, exporter, importer


@exporter(name='COCO', ext='ZIP', version='1.0')
def _export(dst_file, task_data, save_images=False):
    extractor = CvatTaskDataExtractor(task_data, include_images=save_images)
    extractor = Dataset.from_extractors(extractor) # apply lazy transforms
    with TemporaryDirectory() as temp_dir:
        converter = dm_env.make_converter('coco_instances',
            save_images=save_images)
        converter(extractor, save_dir=temp_dir)

        make_zip_archive(temp_dir, dst_file)

@importer(name='COCO', ext='JSON, ZIP', version='1.0')
def _import(src_file, task_data):
    src_path = src_file.name

    if src_path.lower.endswith('.json'):
        dataset = dm_env.make_extractor('coco_instances', src_path)
        import_dm_annotations(dataset, task_data)
    else:
        with TemporaryDirectory() as tmp_dir:
            Archive(src_path).extractall(tmp_dir)

            dataset = dm_env.make_importer('coco')(tmp_dir).make_dataset()
            import_dm_annotations(dataset, task_data)
