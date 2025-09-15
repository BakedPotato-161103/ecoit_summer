import numpy
import torch 
from torch import nn
from torch.nn import functional as F
from torchvision.transforms import functional as vF
from collections.abc import Callable, Hashable, Mapping, Sequence

class MappedFunction(nn.Module):
    def __init__(self, func: Callable):
        super().__init__()
        self.func = func
    
    def forward(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class FixedResize(nn.Module): 
    def __init__(self, shape):
        super().__init__()
        self.shape = shape
        assert sum(self.shape) > 0, "Cannot do imaginary scaling"
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        input_dim = x.shape[1:]
        output_dim = []
        for i, dim in enumerate(self.shape):
            if dim == -1: 
                index = 1 - i
                dim = int(self.shape[index] / input_dim[index] * input_dim[i])
            output_dim.append(dim)
        return vF.resize(x, output_dim)
    