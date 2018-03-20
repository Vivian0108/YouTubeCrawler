import random
import sys

def get_times(time_text):
    times = time_text.split('-->')
    if len(times) != 2:
        raise Exception('Time format incorrect')
    start_time = times[0].strip().split(':')
    start_time = int(start_time[0]) * 3600 + \
                 int(start_time[1]) * 60 + \
                 float(start_time[2][:6])
    end_time = times[1].strip().split(':')
    end_time = int(end_time[0]) * 3600 + \
               int(end_time[1]) * 60 + \
               float(end_time[2][:6])
    return (start_time, end_time)

def raw_parse(filename):
    time_and_words = []
    current_time = None
    current_text = []
    with open(filename, 'r') as f:
        for row in f:
            if ('WEBVTT' in row or
                'Kind: captions' in row or
                'Language: en' in row or
                row.strip() == ''):
                   continue
            if '-->' in row:
                if len(current_text) > 0:
                    raise Exception('Text without time')
                current_time = get_times(row)
            else:
                current_text.append(row.strip())
                if current_time:
                    (start, end) = current_time
                    time_and_words.append((' '.join(current_text), start, end))
                    current_text = []
    if len(time_and_words) == 0:
        raise Exception('Transcript problematic')
    return time_and_words

def group_sentences(filename):
    time_and_words = raw_parse(filename)
    sentence_times = []
    current_start_time = None
    for (text, start, end) in time_and_words:
        if text[-1] == '?' or text[-1] == '.' or text[-1] == '!':
            if current_start_time:
                sentence_times.append((current_start_time, end))
                current_start_time = None
            else:
                sentence_times.append((start, end))
        else:
            if not current_start_time:
                current_start_time = start
    # use the end of the video as the last end time if no sentence ends there
    if current_start_time:
        sentence_times.append((current_start_time, time_and_words[-1][-1]))
    return sentence_times

# secs: minimum number of seconds for one segment
def get_random_segment(secs, filename):
    groups = group_sentences(filename)
    last_end_time = groups[-1][1]
    latest_start_time = last_end_time - secs
    latest_existing_start_time_ind = None
    for i in range(len(groups)):
        (start, _) = groups[i]
        if start < latest_start_time:
            latest_existing_start_time_ind = i
        else:
            break
    if not latest_existing_start_time_ind:
        return ((groups[0][0], groups[-1][-1]), 
                (groups[0][0], groups[-1][-1]))
    random_start_time = random.choice(groups[:i])[0]
    earliest_end_time = random_start_time + secs
    end_time = None
    for (_, end) in groups:
        if end > earliest_end_time:
            end_time = end
            break
    if not end_time:
        raise Exception('Timing error')
    return ((groups[0][0], groups[-1][-1]), (random_start_time, end_time))

if __name__ == '__main__':
    print(get_random_segment(120, sys.argv[1]))
