from dataclasses import dataclass
from typing import Optional, Union, Any, TYPE_CHECKING, Sequence
from ..ngff_versions import NGFFVersion

if TYPE_CHECKING:
    from ..v05 import Metadata as Metadata_v05
    from ..v06 import Metadata as Metadata_v06

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
    scale: Sequence[float]
    type: str = "scale"

@dataclass(kw_only=True)
class Translation(Transform):
    translation: Sequence[float]
    type: str = "translation"

@dataclass
class Dataset:
    path: str
    coordinateTransformations: Union[Sequence[Scale], Sequence[Scale | Translation]]

@dataclass
class MethodMetadata:
    description: Optional[str] = ""
    method: Optional[str] = ""
    version: Optional[str] = ""
    args: Optional[Sequence[Any]] = None
    kwargs: Optional[dict[str, Any]] = None

@dataclass
class Metadata:
    axes: Sequence[Axis]
    datasets: Sequence[Dataset]
    version: NGFFVersion | str = NGFFVersion.V04
    name: str | None = "image"
    coordinateTransformations: Optional[Sequence[Transform]] = None
    labels: str | None = None
    type: Optional[str] = None
    metadata: Optional[MethodMetadata] = None

    def to_version(self, version: NGFFVersion | str) -> Union["Metadata", "Metadata_v05", "Metadata_v06"]:
        if isinstance(version, str):
            version = NGFFVersion(version)

        if version == NGFFVersion.V04:
            return self
        elif version == NGFFVersion.V05:
            return self._to_v05()
        elif version == NGFFVersion.V06:
            from ..v06 import Metadata as Metadata_v06
            return Metadata_v06.from_version(self)
        else:
            raise ValueError(f"Unsupported conversion from version {self.version} to {version}")

    @classmethod
    def from_version(cls, metadata: Union["Metadata", "Metadata_v05", "Metadata_v06"]) -> "Metadata":
        if isinstance(metadata, "Metadata"):
            return metadata
        elif isinstance(metadata, "Metadata_v05"):
            return cls._from_v05(metadata)
        elif isinstance(metadata, "Metadata_v06"):
            raise NotImplementedError("Conversion from v0.6 to v0.4 is not implemented yet")
    
    def _to_v05(self) -> "Metadata_v05":
        from ..v05 import Metadata as Metadata_v05, Dataset

        datasets = []
        for ds in self.datasets:
            transforms = []
            for t in ds.coordinateTransformations:
                if isinstance(t, Scale):
                    transforms.append(Scale(scale=t.scale))
                elif isinstance(t, Translation):
                    transforms.append(Translation(translation=t.translation))
                else:
                    raise ValueError(f"Unsupported transform type: {t.type}")
            
            datasets.append(
                Dataset(
                    path=ds.path,
                    coordinateTransformations=tuple(transforms)
                )
            )

        return Metadata_v05(
            axes=self.axes,
            datasets=datasets,
            name=self.name,
            coordinateTransformations=self.coordinateTransformations,
            labels=self.labels,
            type=self.type,
            metadata=self.metadata
        )
    
    @classmethod
    def _from_v05(cls, metadata: "Metadata_v05") -> "Metadata":
        datasets = []
        for ds in metadata.datasets:
            transforms = []
            for t in ds.coordinateTransformations:
                if isinstance(t, Scale):
                    transforms.append(Scale(scale=t.scale))
                elif isinstance(t, Translation):
                    transforms.append(Translation(translation=t.translation))
                elif isinstance(t, Transform) and t.type == "identity":
                    transforms.append(Scale(scale=[1.0] * len(metadata.axes)))
                else:
                    raise ValueError(f"Unsupported transform type: {t.type}")
            datasets.append(
                Dataset(
                    path=ds.path,
                    coordinateTransformations=tuple(transforms)
                )
            )
        return cls(
            axes=metadata.axes,
            datasets=datasets,
            name=metadata.name,
            coordinateTransformations=metadata.coordinateTransformations,
            labels=metadata.labels,
            type=metadata.type,
            metadata=metadata.metadata
        )
