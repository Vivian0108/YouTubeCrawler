import os




if __name__ == '__main__':
	for file in os.listdir('../../MMMO/Main/Raw/Audio/Full/'):
		name = file[:-4]
		print 'sudo python align.py ../../MMMO/Main/Raw/Audio/Full/%s.wav ../../MMMO/Main/Raw/Transcript/Full/%s.trs ../../MMMO/Main/Aligned/%s.json' % (name, name, name)