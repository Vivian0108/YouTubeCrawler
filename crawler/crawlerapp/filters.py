from abc import ABC, abstractmethod
import random

class AbstractFilter(ABC):
    @property
    @abstractmethod
    def name(self):
        return self.name

    @property
    @abstractmethod
    def description(self):
        return self.description

    @abstractmethod
    def filter(self, video_ids, download_path):
        pass

class RandFilter(AbstractFilter):
    def name(self):
        return "Random Filter"
    def description(self):
        return "Randomly chooses videos that pass"
    def filter(self, video_ids, download_path):
        num_vids = random.randint(0,len(video_ids)-1)
        chosen_vids = random.sample(video_ids, num_vids)
        return chosen_vids
