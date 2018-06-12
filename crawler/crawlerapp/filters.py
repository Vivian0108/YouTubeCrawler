from abc import ABC, abstractmethod
import random
import time
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


#class AlignFilter(AbstractFilter):
    def name(self):
        return "P2FA Align Video"

    def description(self):
        return "Uses P2FA to align the downloaded videos"

    def check_pratt(pratt_file):
        if not os.path.isfile(pratt_file):
            return False
        lines = []
        with open(pratt_file, 'r') as f:
            lines = f.read().split('\n')
        first_space = 0
        for i in range(len(lines)):
            if 'sp' == lines[i]:
                first_space = i
                break
        lines = lines[first_space - 2:]
        word_timing = []
        space_timing = []
        accumulator = 0
        for i in range(int(len(lines) / 3)):
            start = float(lines[i * 3])
            stop = float(lines[i * 3 + 1])
            phoneme = float(lines[i * 3 + 2])
            if phoneme == 'sp':
                accumulator = 0
                space_timing.append(stop - start)
                word_timing.append(accumulator)
            else:
                accumulator += stop - start

        for time in word_timing:
            if time > 3:
                return False
        for time in space_timing:
            if time > 5:
                return False
        return True

    def align_video(align_data):
        (download_path, video_id) = align_data
        path = download_path
        subprocess.call('ffmpeg -y -loglevel quiet -i %s %s' %
                        (path + '.mp4', path + '.wav'),
                        shell=True)
        lines = []
        with open(path + '.en.vtt', 'r') as f:
            for line in f:
                remove_cond = (
                    'WEBVTT' in line or
                    'Kind: captions' in line or
                    'Language: en' in line or
                    '-->' in line
                )
                if not remove_cond:
                    lines.append(line.strip())

        with open(path + '.plaintext', 'w') as f:
            f.write(' '.join(lines))

        subprocess.call('/home/edmundtemp/sqa/crawler/AZP2FA/p2fa/align.py %s %s %s'
                        % (path + '.wav', path + '.plaintext', path + '.pratt'),
                        shell=True)

        if check_pratt(path + '.pratt'):
            return True
        else:
            return False

    def filter(self, video_ids, download_path):
        align_data = [
            (
                os.path.join(download_path, video_id),
                video_id
            ) for video_id in video_ids
        ]
        succeeded = []
        for tuple in align_data:
            if align_video(tuple):
                succeeded.append(tuple[1])
        return succeeded
