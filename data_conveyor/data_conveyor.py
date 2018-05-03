from random import randint

import cv2
import os

import numpy as np

from data_conveyor.augmentations import augmentations_dict, ToPyTorch


class Dataset:
    def __init__(self, step_type: str, config: {}):
        def get_pathes(directory):
            def make_target(target):
                res = np.zeros(classes_num)
                res[target - 1] = 1
                return target
            res = []
            classes_num = len(classes)
            for cur_class in classes:
                res += [{'path': os.path.join(os.path.join(directory, str(cur_class)), file), 'target': make_target(int(cur_class))}
                        for file in
                        os.listdir(os.path.join(directory, str(cur_class)))]
            return res

        # if step_type == 'test':
        #     self.__pathes =
        # else:
        dir = os.path.join(config['workdir_path'], config['data_conveyor'][step_type]['dataset_path'])
        classes = [int(d) for d in os.listdir(dir)]
        self.__pathes = get_pathes(dir)
        percentage = config['data_conveyor'][step_type]['images_percentage'] if 'images_percentage' in config['data_conveyor'][step_type] else 100
        self.__cell_size = 100 / percentage
        self.__data_num = len(self.__pathes) * percentage // 100
        self.__percentage = percentage
        const_augmentations_config = config['data_conveyor'][step_type]['const_augmentations']
        self.__const_augmentations = [augmentations_dict[aug](const_augmentations_config) for aug in const_augmentations_config.keys()]
        if 'augmentations' in config['data_conveyor'][step_type]:
            augmentations_config = config['data_conveyor'][step_type]['augmentations']
            self.__augmentations = [augmentations_dict[aug](augmentations_config) for aug in augmentations_config.keys()]
        else:
            self.__augmentations = []
        self.__before_output = ToPyTorch()
        self.__augmentations_percentage = config['data_conveyor'][step_type]['augmentations_percentage'] if 'augmentations_percentage' in config['data_conveyor'][step_type] else None

    def __getitem__(self, item):
        def augmentate(image):
            for aug in self.__const_augmentations:
                image = aug(image)
            if self.__augmentations_percentage is not None and randint(1, 100) <= self.__augmentations_percentage:
                for aug in self.__augmentations:
                    image = aug(image)
            return self.__before_output(image)

        item = randint(1, self.__cell_size) + int(item * self.__cell_size) - 1 if self.__percentage < 100 else item

        if 'target' in self.__pathes[item]:
            return {'data': augmentate(cv2.imread(self.__pathes[item]['path'])),
                    'target': self.__pathes[item]['target']}
        else:
            return augmentate(cv2.imread(self.__pathes[item]['path']))

    def __len__(self):
        return self.__data_num