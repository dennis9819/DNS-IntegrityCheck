
class HistoryBuffer:
    buffer = []
    bufferSize = 0
    bufferPointer = 0
    bufferTopPointer = 0
    bufferMaxPointer = -1

    def __init__(self,size):
        self.bufferSize = size

    def append(self,message):
        
        if self.bufferMaxPointer <  self.bufferTopPointer:
            self.buffer.append(message)
            self.bufferMaxPointer += 1
        else:
            self.buffer[self.bufferTopPointer] = message

        self.bufferTopPointer += 1
        if self.bufferTopPointer > self.bufferSize:
            self.bufferTopPointer = 0
        self.bufferPointer = self.bufferTopPointer

    def getPrevious(self,count = 1):
        if count > self.bufferMaxPointer - 2:
            raise ValueError("History to small")
        self.bufferPointer = self.bufferPointer - count
        if self.bufferPointer < 0:
            self.bufferPointer += self.bufferSize
        return self.buffer[self.bufferPointer]

