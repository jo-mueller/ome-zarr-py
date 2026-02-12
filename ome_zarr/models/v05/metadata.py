from dataclasses import dataclass
from typing import Sequence, Union, TYPE_CHECKING

from ..v04 import Axis, MethodMetadata, Transform, Scale, Translation
from ..ngff_versions import NGFFVersion

if TYPE_CHECKING:
    from ..v04 import Metadata as Metadata_v04
    from ..v06 import Metadata as Metadata_v06

@dataclass(kw_only=True)
class Identity(Transform):
    type: str = "identity"

@dataclass
class Dataset:
    path: str
    coordinateTransformations: Union[tuple[Identity,], tuple[Scale,], tuple[Scale, Translation]]

@dataclass
class Metadata:
    axes: Sequence[Axis]
    datasets: Sequence[Dataset]
    name: str | None = "image"
    coordinateTransformations: Sequence[Transform] | None = None
    labels: str | None = None
    type: str | None = None
    metadata: MethodMetadata | None = None
    
    def to_version(self, version: NGFFVersion | str) -> Union["Metadata", "Metadata_v04"]:
        if isinstance(version, str):
            version = NGFFVersion(version)

        if version == NGFFVersion.V04:
            return self._to_v04()
        elif version == NGFFVersion.V05:
            return self
        else:
            raise ValueError(f"Unsupported conversion from version 0.5 to {version}")

    @classmethod
    def from_version(cls, metadata: Union["Metadata_v04", "Metadata_v06"]) -> "Metadata":
        if isinstance(metadata, "Metadata_v04"):
            return cls._from_v04(metadata)
        elif isinstance(metadata, "Metadata_v06"):
            return metadata._to_v05()
        else:
            raise NotImplementedError(f"Conversion from {type(metadata).__name__} to v0.5 is not implemented")
        
    def _to_v04(self) -> "Metadata_v04":
        from ..v04 import Metadata as Metadata_v04
        return Metadata_v04.from_version(self)
    
    @classmethod
    def _from_v04(cls, metadata: "Metadata_v04") -> "Metadata":
        datasets = []
        for dataset in metadata.datasets:
            transforms = []
            for t in dataset.coordinateTransformations:
                if isinstance(t, Scale):
                    transforms.append(Scale(scale=t.scale))
                elif isinstance(t, Translation):
                    transforms.append(Translation(translation=t.translation))
                else:
                    raise ValueError(f"Unsupported transform type: {t.type}")
            datasets.append(
                Dataset(
                    path=dataset.path,
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