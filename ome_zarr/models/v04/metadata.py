from dataclasses import dataclass
from typing import Optional, Union, Any

@dataclass
class Axis:
    name: str
    type: Optional[str] = None
    unit: Optional[str] = None


@dataclass(kw_only=True)
class Transform:
    type: str

@dataclass(kw_only=True)
class Scale(Transform):
    scale: list[float]
    type: str = "scale"

@dataclass(kw_only=True)
class Translation(Transform):
    translation: list[float]
    type: str = "translation"

@dataclass
class Dataset:
    path: str
    coordinateTransformations: Union[tuple[Scale,], tuple[Scale, Translation]]

@dataclass
class MethodMetadata:
    description: Optional[str] = ""
    method: Optional[str] = ""
    version: Optional[str] = ""
    args: Optional[list[Any]] = None
    kwargs: Optional[dict[str, Any]] = None

@dataclass
class Metadata:
    axes: list[Axis]
    datasets: list[Dataset]
    version: str = "0.4"
    name: Optional[str] = "image"
    coordinateTransformations: Optional[list[Transform]] = None
    type: Optional[str] = None
    metadata: Optional[MethodMetadata] = None
    
