import os
from typing import Optional, List
from collections.abc import Callable
from functools import partial
from copy import deepcopy
import random
import json

import numpy as np
import cv2
from PIL import Image

import torch
from torch import nn
from torch.nn import Sequential
import torch.nn.functional as F
from torch.utils.data import ConcatDataset, DataLoader, Dataset, random_split
from torch.utils.data.sampler import Sampler

import torchvision
from torchvision import transforms as T

import rootutils
rootutils.setup_root(search_from=__file__, indicator="setup.py", pythonpath=True)

from src.models.text_rec.data.transform import *
# always starting with vanilla dataset, like its a norm
class EcoitDataset(Dataset):
    """ Base dataset to handle information and linking, direct graphics processing to 'TransformedDataset'
            Arguments:
            - json_path: JSON configuration tailored for this dataset only to link TextDetection to Recognition models
    """
    def __init__(self,
                 json_path: str = "",
                 sorted: bool = True
                 ):
        super().__init__()
        self.data_dir = ""
        if json_path == "":
            raise AssertionError("No dataset ?")
        self.setup(json_path, sorted)
    
    def setup(self, json_path, sorted_ratios=False):
        json_object = json.load(open(json_path, "r"))
        self.data_dir = json_object['data_dir']
        self.name = json_object['name']
        self.objects = json_object['objects']
        self.data = list(json_object['objects'].keys())
        if sorted_ratios:
            ratios = []
            for index, key in enumerate(self.data):
                geometry = self.objects[key]['det']
                w, h = geometry[1][0] - geometry[0][0], geometry[1][1] - geometry[0][1]
                ratios.append((index, w/h))
            sorted_ratios = sorted(ratios, key=lambda temp: temp[1])
            self.data = [self.data[idx] for idx, _ in sorted_ratios]
    
    def get_item(self, index: int):
        key = self.data[index]
        output = deepcopy(self.objects[key])
        output["image"] = os.path.join(self.data_dir, output["image"])
        output["id"] = key
        return output
    
    # In case they query in list of index
    def __getitem__(self, index):
        output = None
        if not isinstance(index, int):
            output = []
            for id in index:
                output.extend(self.get_item(id))
        else:
            output = self.get_item(int(index))
        
        return output
    
    def __len__(self) -> int:
        return len(self.data)

class TransformedDataset(Dataset):
    """ Handling image and multimedia for torch
    """
    def __init__(self, dataset: Dataset, transform: Sequential | T.Compose | None = None):
        super().__init__()
        self.dataset = dataset
        self.transform = transform if transform else Sequential(
                                                                MappedFunction(partial(Image.open)),
                                                                MappedFunction(T.ToTensor()),
                                                                FixedResize(shape=[32, -1]),
                                                                T.CenterCrop([32, 512]),
                                                                T.Normalize(mean=(0.485, 0.456, 0.406),
                                                                            std=(0.229, 0.224, 0.225),
                                                                            )
                                                                )
        
    def __getitem__(self, index):
        obj = deepcopy(self.dataset[index])
        obj["image"] = self.transform(obj["image"])
        return obj

    def __len__(self):
        return len(self.dataset)

class Collator(Callable):
    def __init__(self, h, min_w, max_w, image_key="image"):
        super().__init__()
        self.h = h
        self.min_w = min_w
        self.max_w = max_w
        self.image_key = image_key
    
    def __call__(self, batch):
        output = dict()
        for key in batch[0].keys():
            output[key] = [it[key] for it in batch]
        max_w = max([im.shape[-1] for im in output])
         

if __name__ == "__main__":
    dataset = EcoitDataset("data/temp/json/detection.json", sorted=True)
    transformed_dataset = TransformedDataset(dataset)
    dataloader = DataLoader(transformed_dataset, batch_size=4, shuffle=False, num_workers=4)
    dataloader = iter(dataloader)
    batch = next(dataloader)
    import IPython
    IPython.embed()
