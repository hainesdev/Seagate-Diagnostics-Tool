import sys
import glob
# import pip
# pip install --user pyserial
import serial
#import time
import re

welcome = []
welcome.append("  ______   ______   ______   ______   ______   ______   ______ \n")
welcome.append(" /_____/  /_____/  /_____/  /_____/  /_____/  /_____/  /_____/ \n")
welcome.append("                                                               \n")
welcome.append("                                                               \n")
welcome.append("       _________                            __                 \n")
welcome.append("      /   _____/ ____ _____     _________ _/  |_  ____         \n")
welcome.append("      \\_____  \\_/ __ \\\\__  \\   / ___\\__  \\\\   __\\/ __ \\        \n")
welcome.append("      /        \\  ___/ / __ \\_/ /_/  > __ \\|  | \\  ___/        \n")
welcome.append("     /_______  /\\___  >____  /\\___  (____  /__|  \\___  >       \n")
welcome.append("             \\/     \\/     \\//_____/     \\/          \\/        \n")
welcome.append("    ____ ___      .__                 __                ._.    \n")
welcome.append("   |    |   \\____ |  |   ____   ____ |  | __ ___________| |    \n")
welcome.append("   |    |   /    \\|  |  /  _ \\_/ ___\\|  |/ // __ \\_  __ \\ |    \n")
welcome.append("   |    |  /   |  \\  |_(  <_> )  \\___|    <\\  ___/|  | \\/\\|    \n")
welcome.append("   |______/|___|  /____/\\____/ \\___  >__|_ \\\\___  >__|   __    \n")
welcome.append("                \\/                 \\/     \\/    \\/       \\/    \n")
welcome.append("                                                               \n")
welcome.append("                                                               \n")
welcome.append("  ______   ______   ______   ______   ______   ______   ______ \n")
welcome.append(" /_____/  /_____/  /_____/  /_____/  /_____/  /_____/  /_____/ \n")
welcome.append("                                                               \n")
welcome.append("Created by Dan Haines\n")
welcome.append("Use this program at your own risk! I accept no liability.\n")
welcome.append("This code is intended to be used only with a locked ST310014ACE.\n")
welcome.append("This tool is able to read the lock sector, wipe it and write it.\n")
welcome = "".join(welcome)

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def ascii_bytes(cmd):
    return bytes(cmd.encode('ascii'))

class serial_stream:
    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.port = port
        self.ser.open()
        self.stream = []    # creates a new empty list for each dog
        self.in_count = 0
    def close(self):
        self.ser.close()
    def count_in(self):
        resp = "".join(self.stream)
        found = len(re.findall(">", resp))
        found += len(re.findall("PSlv", resp))
        return found

    def send_command(self, command, ret='\r'):
        self.ser.timeout = 0
        before_com = len(self.stream)
        #send one character at a time
        length = len(command)
        command = command + ret
        for char in range(0, length):
            self.ser.write(ascii_bytes(command[char]))
            rd = self.ser.read(1)
            self.stream.append(str(rd.decode('ascii')))
        self.ser.write(ascii_bytes(ret))
        #Wait until command has processed
        self.in_count += 1
        count = self.count_in()
        while(self.in_count > count):
            #print(1)
            #print(str(self.in_count) + ' : ' + str(count))
            #print("stream: ")
            #print("".join(self.stream))
            count = self.count_in()
            rd = self.ser.read(1)
            self.stream.append(rd.decode('ascii'))
            if(self.in_count < count):
                self.in_count = count
        self.in_count = count
        #Wait for any remaining input that may have been missed
        while(self.ser.in_waiting > 0):
            line = self.ser.readline(1).decode('ascii')
            self.stream.append(line)
        #update count once again
        count = self.count_in()
        if(self.in_count < count):
            self.in_count = count
        output = "".join(self.stream[before_com : len(self.stream)])
        print(output)
        return output
    def read_lock_key(self):
        self.send_command('\x03')
        self.send_command('\x1A')
        self.send_command('/2')
        self.send_command('S006b')
        self.send_command('R20,01')
        self.send_command('C0,570')
        key_log = self.send_command('B570')
        lock_lines = key_log.splitlines()
        lock_lines.pop(0)
        lock_lines.pop(0)
        lock_lines.pop(0)
        clean_lines = []
        for lines in lock_lines:
            clean_lines.append(lines[6:78].strip())
        cleaner_lines = "".join(clean_lines)
        cleaner_lines = cleaner_lines.replace(" ", "")
        #   Just the hex key    #################################
        #key_log = key_log.replace(" ", "")
        #start_pos = re.search('0AE02000000000', key_log).span()[1]
        #key_span = slice(start_pos, start_pos+40)
        #return key_log[key_span]
        #########################################################
        return cleaner_lines
    def clear_lock_key(self):
        self.send_command('\x03')
        self.send_command('\x1A')
        self.send_command('/2')
        self.send_command('S006b')
        self.send_command('R21,01')
        self.send_command('C0,570')
        self.send_command('W20,01')
        return "Lock sector has been cleared. The drive is now unlocked!"
    def write_lock_key(self, key):
        #print(key)
        #go to level 2
        self.send_command('\x03')
        self.send_command('\x1A')
        self.send_command('/2')
        self.send_command('S006b')
        self.send_command('R20,01')
        self.send_command('C0,570')
        self.send_command('/1')
        self.send_command("UA,E000")      
        #Make changes to HDD buffer
        length = len(key)
        for word in range(0, length, 2): 
            pos = slice(word, word+2)
            self.send_command(key[pos], '\n')
        #ctrl+z
        self.send_command('\x1A')  
        #write changes to disk
        self.send_command('/2')
        self.send_command('W20,01')
        #display the buffer that was written
        #self.send_command('/1')
        #print("".join(self.send_command("B570")))
        return "Lock sector has been written. The drive is now locked!"
if __name__ == '__main__':
    print(welcome)
    print("Available COM Ports:")
    ports = serial_ports()
    x = 0
    for port in ports:
        x+=1
        print(str(x) + ". " + port)
    selection = input("Select your COM port: ")
    port = ports[int(selection)-1]
    terminal = serial_stream(port)
    exit = False
    while exit == False:
        print("\nYou will likely want to do these procedures in order.")
        print("You must store the lock sector if you intend to relock the drive with the original key.")
        print("After your entry you will see the commands issued and output\n")
        print("1. Read the lock sector and output it to lock_sector.txt")
        print("2. Clear the lock sector and put the drive in an unlocked state")
        print("3. Write the lock sector the the drive stored in lock_sector.txt")
        selection =input("Selection: ")
        if selection == '1':
            print("Reading lock sector:")
            lock_sector = terminal.read_lock_key()
            print("Writing to lock_sector.txt")
            lockfile = open("lock_sector.txt", "w")
            lockfile.write(lock_sector)
            lockfile.close()
            continue
        elif selection == '2':
            print("clearing lock: ")
            print(terminal.clear_lock_key())
            continue
        elif selection == '3':
            print("Opening lock_sector.txt")
            lockfile = open("lock_sector.txt", "r")
            locksector = lockfile.read()
            print("writing lock: ")
            print(terminal.write_lock_key(locksector))
            continue
        exit = True
        break
    terminal.close()
