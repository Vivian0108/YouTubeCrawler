
def align(file):
    raw_transcript = open(file,"r")
    sections = raw_transcript.read().split("\n\n")
    line_count = 0
    #times are on even lines on even segments and odd lines on odd segments
    segment = 0

    intervals = []
    features = []

    for section_num, section in enumerate(sections):
        if section_num > 0:
            try:
                times = section.split("\n")[0]
                words = section.split("\n")[1]
            except IndexError:
                #Empty line
                continue

            line_time = 0
            #At time stamp

            start_time = times[:12].replace(":","")
            end_time = times[17:].replace(":","")

            start_hours = start_time[0:2]
            start_minutes = start_time[2:4]
            start_seconds = start_time[4:10]
            start_total = float(start_hours)*3600+float(start_minutes)*60+float(start_seconds)

            end_hours = end_time[0:2]
            end_minutes = end_time[2:4]
            end_seconds = end_time[4:10]
            end_total = float(end_hours)*3600+float(end_minutes)*60+float(end_seconds)

            line_time = end_total - start_total

            letters = words.replace(" ", "")
            if len(letters) == 0:
                continue
            increment = line_time/len(letters)

            start = start_total
            end = start_total + increment
            for index,letter in enumerate(letters):
                interval = [start,end]
                intervals.append(interval)
                features.append(letter)
                start = end
                end = end+increment

    return intervals,features
