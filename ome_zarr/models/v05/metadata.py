from dataclasses import dataclass
from typing import Optional, Union

from ..v04 import Axis, MethodMetadata, Transform, Scale, Translation

@dataclass(kw_only=True)
class Identity(Transform):
    type: str = "identity"

@dataclass
class Dataset:
    path: str
    coordinateTransformations: Union[tuple[Identity,], tuple[Scale,], tuple[Scale, Translation]]

@dataclass
class Metadata:
    axes: list[Axis]
    datasets: list[Dataset]
    version: str = "0.5"
    name: Optional[str] = "image"
    coordinateTransformations: Optional[list[Transform]] = None
    type: Optional[str] = None
    metadata: Optional[MethodMetadata] = None
    
