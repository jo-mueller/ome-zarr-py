from ..v05 import Axis, MethodMetadata
from dataclasses import dataclass
from typing import Optional

@dataclass
class coordinateSystem:
  name: str
  axes: list[Axis]

@dataclass(kw_only=True)
class BaseTransform:
  type: str
  name: str
  input: coordinateSystem | str
  output: coordinateSystem | str

@dataclass(kw_only=True)
class Identity(BaseTransform):
  type: str = "identity"

@dataclass(kw_only=True)
class Scale(BaseTransform):
  type: str = "scale"
  scale: list[float]

@dataclass(kw_only=True)
class Translation(BaseTransform):
  type: str = "translation"
  translation: list[float]

@dataclass
class Dataset:
  path: str
  coordinateTransformations: tuple[Identity,] | tuple[Scale,] | tuple[Scale, Translation]

@dataclass
class Metadata:
  coordinateSystems: list[coordinateSystem]
  datasets: list[Dataset]
  version: str = "0.6"
  name: str = "image"
  coordinateTransformations: Optional[list[BaseTransform]] = None
  type: Optional[str] = None
  metadata: Optional[MethodMetadata] = None
    