from abc import ABCMeta, abstractmethod
from pathlib import Path
from json import load, dump

class ParamAbstract(metaclass=ABCMeta):
	def __init__(self, **kwargs):
		self.data: dict = kwargs

	@classmethod
	def from_config(cls, config: Path):
		return cls(**load(config.open('r')))

	@classmethod
	def from_dict(cls, **data):
		return cls(**data)

	@abstractmethod
	def write_to_config(self, name): pass

	@abstractmethod
	def generate_config_name(self): pass

class DemucsParam(ParamAbstract):

	def write_to_config(self, name=""):
		if self.data == {}:
			raise Exception("No data to write to config")
		with open('presets_demucs.json', 'w') as f:
			dump({name if name != "" else self.generate_config_name(): self.data}, f, indent=4)
			return Path('presets_demucs.json').absolute()



	def generate_config_name(self):
		pass