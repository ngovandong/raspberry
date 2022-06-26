import pyaudio
import wave
import time
import datetime
import os

inso = ['', 'Mot ', 'Hai ', 'Ba ', 'Bon ', 'Nam ', 'Sau ', 'Bay ', 'Tam ', 'Chin ']
hauto = ['', 'Nghin ']
thu = ['Chu Nhat ', 'Thu Hai ', 'Thu Ba ', 'Thu Tu ', 'Thu Nam ', 'Thu Sau ', 'Thu Bay ']

DEFAULT_SAVE_FILENAME = 'temp.wav'
DEFAULT_PLAY_FILENAMES = [
    'recordedAudio.wav',
    'hello.wav',
    'goodbye.wav',
    'story.wav',
    'music.wav',
]
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 16000

def num_to_vie_str (x):
    string = '';
    less_than_ten = False
    t=100
    n=0
    if(x<10):
        string += inso[x] 
        less_than_ten = True
    while(x>=1 and less_than_ten == False):
        prev_n = n
        n = int(x/t)
        if(n==5 and t==1):
            string += 'Lam '
            break
        if(n==1 and t==1 and prev_n > 1):
            string += 'Most '
            break
        if(n==4 and t==1 and prev_n >= 2):
           string += 'Tu '
           break
        if(n>1 or t!=10):
            string += inso[n]
        if(t==100 and n!=0):
            string += "Tram " 
        elif(t==10 and n<2 and n>0):
            string += "Muoif "
        elif(t==10 and n>=2):
            string += "Muoi "
        else:
            string = string 
        if(t==10 and n==0):
            string += "Le "
        x-=n*t
        t/=10
    return string

def read_num(n):
    i = 0
    A = [0,0]
    result = ''
    n = int(n)
    if(n == 0):
        result += 'Khong '
    while(n>=1):
        A[i] = n%1000
        i = i + 1 
        n = int(n/1000)
    for j in range (i-1, -1, -1):
        result += num_to_vie_str(A[j])
        if(A[j]!=0):
            result += hauto[j]
    return result

timeout = 60000
class AudioControl:
    def __init__(self):
        self.isRecording = False
        self.isPlaying = False
        self.p = pyaudio.PyAudio()
        self.streamPlay = None
        self.streamRecord = None
        self.wf = None

    def force_stop(self):
        self.stop_playback()

    def callbackPlay(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    def callbackRecord(self, in_data, frame_count, time_info, status):
        self.wf.writeframes(in_data)
        return (in_data, pyaudio.paContinue)

    def start_recording(self, file_name):
        try:
            print(">>> start recording")
            #open wave file to write
            #if(self.isPlaying):
                #self.stopPlayback()
            self.wf = wave.open(file_name, 'wb')
            self.wf.setnchannels(channels)
            self.wf.setsampwidth(self.p.get_sample_size(format))
            self.wf.setframerate(rate)

            self.streamRecord = self.p.open(format = format,
                            channels = channels,
                            rate = rate,
                            input = True,
                            frames_per_buffer = chunk,
                            stream_callback= self.callbackRecord)
            #create frames for recording
            self.streamRecord.start_stream()
        
        except ValueError as e:
            print(e)

    def stop_recording(self):
        try:
            if self.streamRecord:
                # Close the audio recording stream
                self.streamRecord.stop_stream()
                print ("stop_recording()> Recording stopped")
                # write data to WAVE file
                self.streamRecord.close()
                self.wf.close()
                self.isRecording = False
                self.resetThread()

        except ValueError as e:
            print(e)

    def start_playback(self, file_name, wait = False):
        try:
            print(">>> start playing audio")
            self.wf = wave.open(file_name, 'rb')
            # open stream based on the wave object which has been input.
            self.streamPlay = self.p.open(format =
                            self.p.get_format_from_width(self.wf.getsampwidth()),
                            channels = self.wf.getnchannels(),
                            rate = self.wf.getframerate(),
                            output = True,
                            stream_callback= self.callbackPlay)

            # start the stream (4)
            self.streamPlay.start_stream()
            if wait:
                while self.streamPlay.is_active():
                    time.sleep(0.2)
                self.stop_playback()
        except ValueError as e:
            print(e)  
    
    def stop_playback(self):
        try:
            if self.streamPlay:
                # stop stream (6)
                self.streamPlay.stop_stream()
                self.streamPlay.close()
                self.wf.close()
                # close PyAudio (7)
                self.p.terminate()
                self.isPlaying = False
                self.resetThread()

        except ValueError as e:
            print(e)

    # def hello(self):
    #     self.start_playback(1)

    def talk(self):
        self.start_playback("story.wav", True)

    def music(self, music, wait = False):
        self.start_playback(music, wait)
    
    def time(self):
        os.remove("time.wav")
        infiles = []
        outfile = "time.wav"
        data= [] 
        time_string = datetime.datetime.now()
        print('Time now: ', time_string)
        time_formatted = time_string.strftime('%H %M %w %d %m %Y')
        result = 'xtb '
        array = time_formatted.split(" ")
        index = 0
        for i in array:
            if index == 0:
                result += read_num(i) + 'gio '
            if index == 1:
                result += read_num(i) 
            if index == 2:
                result += thu[int(i)]
            if index == 3:
                result += 'Ngay ' + read_num(i)
            if index == 4:
                result += 'Thang ' + read_num(i)
            if index == 5:
                result += 'Nam ' + read_num(i)
            index = index + 1
        # print(result)
        result_arr = result.split(' ')
        result_arr = result_arr[0: -1]
        for word in result_arr:
            self.force_stop()
            file = './daytime_speech/{}.wav'.format(word.lower())
            infiles.append(file)
        for infile in infiles:
            w = wave.open(infile, 'rb')
            data.append( [w.getparams(), w.readframes(w.getnframes())] )
            w.close()
        output = wave.open(outfile, 'wb')
        output.setparams(data[0][0])
        for i in range(len(data)):
            output.writeframes(data[i][1])
        output.close()
        self.start_playback(outfile, True)

        
    def resetThread(self):
        self.wf = None
        self.streamRecord = None
        self.streamPlay = None
        self.p = pyaudio.PyAudio()
