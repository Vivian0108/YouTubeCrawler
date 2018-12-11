import os




if __name__ == '__main__':
	for file in os.listdir('../../MOSI/Raw/Audio/WAV_16000/Full'):
		name = file[:-4]
		print 'sudo python align.py ../../MOSI/Raw/Audio/WAV_16000/Full/%s.wav ../../MOSI/Raw/Transcript/Full/%s.textonly ../../MOSI/Aligned/%s.json' % (name, name, name)