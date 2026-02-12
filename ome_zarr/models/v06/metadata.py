from ..v05 import Axis, MethodMetadata
from dataclasses import dataclass
from typing import Optional, Union, TYPE_CHECKING

from ..ngff_versions import NGFFVersion

if TYPE_CHECKING:
  from ..v04 import Metadata as Metadata_v04
  from ..v05 import Metadata as Metadata_v05

@dataclass
class CoordinateSystem:
  name: str
  axes: list[Axis]

@dataclass(kw_only=True)
class BaseTransform:
	type: str
	name: str | None = None
	input: CoordinateSystem | str | None = None
	output: CoordinateSystem | str | None = None

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

@dataclass(kw_only=True)
class Rotation(BaseTransform):
	type: str = "rotation"
	rotation: list[list[float]]	# rotation matrix

@dataclass(kw_only=True)
class Sequence(BaseTransform):
	type: str = "sequence"
	transformations: list[BaseTransform]

@dataclass
class Dataset:
	path: str
	coordinateTransformations: tuple[Identity, ...] | tuple[Scale, ...] | tuple[Sequence, ...]

@dataclass
class Metadata:
	coordinateSystems: list[CoordinateSystem]
	datasets: list[Dataset]
	name: str | None = "image"
	coordinateTransformations: list[BaseTransform] | None = None
	labels: str | None = None
	type: str | None = None
	metadata: MethodMetadata | None = None
	
	def to_version(self, version: NGFFVersion | str) -> Union["Metadata", "Metadata_v04", "Metadata_v05"]:
		if isinstance(version, str):
			version = NGFFVersion(version)

		if version == NGFFVersion.V06:
			return self
		elif version == NGFFVersion.V05:
			return self._to_v05()
		else:
			raise ValueError(f"Unsupported conversion from version 0.6 to {version}")

	@classmethod
	def from_version(cls, metadata: Union["Metadata_v05", "Metadata_v04"]) -> "Metadata":
		if isinstance(metadata, "Metadata_v05"):
			return cls._from_v05(metadata)
		elif isinstance(metadata, "Metadata_v04"):
			return cls._from_v05(Metadata_v05.from_version(metadata))
		else:
			raise NotImplementedError(f"Unsupported conversion to v0.6 from version {metadata.version}")

	@classmethod
	def _from_v05(cls, metadata: "Metadata_v05") -> "Metadata":
		from ..v05 import (
			Scale as Scale_v05,
			Translation as Translation_v05,
			Identity as Identity_v05
		)
		coordinate_systems = [
			CoordinateSystem(
				name='physical',
				axes=metadata.axes
				)
			]

		datasets = []
		for idx, ds in enumerate(metadata.datasets):
			transforms = []
			for t in ds.coordinateTransformations:
				if isinstance(t, Identity_v05):
					transforms.append(
						Identity()
					)
				elif isinstance(t, Scale_v05):
					transforms.append(
						Scale(scale=t.scale)
					)
				elif isinstance(t, Translation_v05):
					transforms.append(
						Translation(translation=t.translation)
					)
				else:
					raise ValueError(f"Unsupported transform type: {t.type}")
					
			if len(transforms) == 2:
				transforms = [
					Sequence(
						name=f"scale{idx}_to_{coordinate_systems[0].name}",
						input=ds.path,
						output=coordinate_systems[0].name,
						transformations=transforms
					)
				]

			datasets.append(
				Dataset(
					path=ds.path,
					coordinateTransformations=tuple(transforms)
				)
			)

		# handle additional coordinate transformations 
		# (non-multiscales datasets)
		coordinateTransformations: list[BaseTransform] = []
		if metadata.coordinateTransformations and len(metadata.coordinateTransformations) > 0:
			cs_target = CoordinateSystem(
				name="output",
				axes=metadata.axes
			)
			coordinate_systems.append(cs_target)
			for t in metadata.coordinateTransformations:
				if isinstance(t, Identity_v05):
					coordinateTransformations.append(
						Identity()
					)
				elif isinstance(t, Scale_v05):
					coordinateTransformations.append(
						Scale(
							scale=t.scale,
						)
					)
				elif isinstance(t, Translation_v05):
					coordinateTransformations.append(
						Translation(
							translation=t.translation,
						)
					)
				else:
					raise ValueError(f"Unsupported transform type: {t.type}")
					
			if len(coordinateTransformations) == 2:
				coordinateTransformations = [
					Sequence(
						name=f"{coordinate_systems[0].name}_to_{cs_target.name}",
						input=coordinate_systems[0].name,
						output=cs_target.name,
						transformations=coordinateTransformations
					)
				]
			elif len(coordinateTransformations) == 1:
				coordinateTransformations[0].input = coordinate_systems[0].name
				coordinateTransformations[0].output = cs_target.name

		return cls(
			coordinateSystems=coordinate_systems,
			datasets=datasets,
			name=metadata.name,
			coordinateTransformations=coordinateTransformations,
			labels=metadata.labels,
			type=metadata.type,
			metadata=metadata.metadata
		)
	
	def _to_v05(self) -> "Metadata_v05":
		from ..v05 import Metadata as Metadata_v05, Dataset
		from ..v05 import (
			Scale as Scale_v05,
			Translation as Translation_v05,
			Identity as Identity_v05
		)

		# parse datasets and extract coordinate transformations
		datasets = []
		for ds in self.datasets:
			transforms = []
			for t in ds.coordinateTransformations:
				if isinstance(t, Identity):
					transforms.append(Identity_v05())
				elif isinstance(t, Scale):
					transforms.append(Scale_v05(scale=t.scale))
				elif isinstance(t, Translation):
					transforms.append(Translation_v05(translation=t.translation))
				elif isinstance(t, Sequence):
					for st in t.transformations:
						if isinstance(st, Identity):
							transforms.append(Identity_v05())
						elif isinstance(st, Scale):
							transforms.append(Scale_v05(scale=st.scale))
						elif isinstance(st, Translation):
							transforms.append(Translation_v05(translation=st.translation))
		
		datasets.append(
			Dataset(
				path=ds.path,
				coordinateTransformations=tuple(transforms)
			)
		)

		# get coordinate system that is used as output for the dataset transforms (if any)
		output_cs_name = transforms[0].output
		outut_cs = [
			cs for cs in self.coordinateSystems if cs.name == output_cs_name
			][0]
		
		# coerce additional transformations to v05 transforms (if any)
		return Metadata_v05(
			axes=outut_cs.axes,
			datasets=datasets,
			name=self.name,
			coordinateTransformations=None,  # TODO: handle non-dataset coordinate transformations
			labels=self.labels,
			type=self.type,
			metadata=self.metadata
		)
	
