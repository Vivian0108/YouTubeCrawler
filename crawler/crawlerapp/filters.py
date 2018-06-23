from abc import ABC, abstractmethod
import random
import time, os, subprocess
from crawlerapp.definitions import CONFIG_PATH
#from AZP2FA.p2fa.align_mod import align


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
        num_vids = random.randint(0, len(video_ids) - 1)
        chosen_vids = random.sample(video_ids, num_vids)
        return chosen_vids


class FilterDemo(AbstractFilter):
    def name(self):
        return "Filter Demo"

    def description(self):
        return "Picks first half of the videos"

    def filter(self, video_ids, download_path):
        time.sleep(5)
        return video_ids[0:len(video_ids) // 2]


class AlignFilter(AbstractFilter):
    def name(self):
        return "P2FA Align Video"

    def description(self):
        return "Uses P2FA to align the downloaded videos"

    def filter(self, video_ids, download_path):
        print(video_ids)
        print(download_path)
        for video in video_ids:
            print("Trying " + video)
            video_dir = os.path.join(download_path, video)
            mp4_path = os.path.join(video_dir, video + ".mp4")
            vtt_path = os.path.join(video_dir, video + ".en.vtt")
            plaintext_path = os.path.join(video_dir, video + ".plaintext")
            wav_path = os.path.join(video_dir, video + ".wav")
            pratt_path = os.path.join(video_dir, video + ".pratt")
            output_file = os.path.join(video_dir, video + ".TextGrid")
            align_path = os.path.join(CONFIG_PATH, os.path.join("AZP2FA", os.path.join("p2fa", os.path.join("align.py"))))
            lines = []
            with open(vtt_path, 'r') as f:
                for line in f:
                    remove_cond = (
                        'WEBVTT' in line or
                        'Kind: captions' in line or
                        'Language: en' in line or
                        '-->' in line
                    )
                    if not remove_cond:
                        lines.append(line.strip())

            with open(plaintext_path, 'w') as f:
                f.write(' '.join(lines))
            subprocess.call(align_path + ' %s %s %s'
                            % (wav_path, plaintext_path, pratt_path),
                            shell=True)
