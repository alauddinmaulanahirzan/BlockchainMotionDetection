# Blockchain Section
from Blockchain import Blockchain
# Firebase Section
from FirebaseHandler import FirebaseHandler
# Camera Section
from CameraHandler import *
# Telemetry Section
from Telemetry import *
# Additional Section
import os
import time
from datetime import datetime

# Hyper Parameters
ref = None
bucket = None
process = None
record_lock = False
counter = 0
hash = None

def runDetection():
    global ref,bucket,process,record_lock,counter
    # Main Parameters
    camera = None
    frame1 = None
    frame2 = None
    motion = False
    record_timer = 0
    timer = 0
    id = 1
    # Detection Start
    print("==> Opening Camera",end="",flush=True)
    camera = CameraHandler.initCamera() # Open Camera
    print(" > [DONE]")
    print("\n==> Detection > [READY]")
    # Start Loop
    while(True):
        # Cooldown Timer
        if(id>200):
            break
        elif(record_lock == True):
            if(timer==5):
                print("\n==> Lock Released")
                print("==> Reseting Record Parameters",end="",flush=True)
                record_lock = False
                timer = 0
                frame1 = None
                frame2 = None
                motion = False
                print(" > [DONE]")
                print("==> Detection > [RESTARTED]")
                print("\n==> Detection > [READY]")
            else:
                print(f"====> Releasing Lock in {150-timer}s",end="\r")
                timer += 1
                time.sleep(1)
        elif(record_lock == False):
            start_milli = current_milli_time()
            percentage  = 0
            # Detect Motion
            frame = CameraHandler.getFrame(camera)
            if(frame1 is None):
                frame1 = frame
            else:
                frame2 = frame
                motion,percentage = CameraHandler.doCompare(frame1,frame2,motion)
                frame1 = frame2
            if(motion==True):
                print("\n==> Motion Detected")
                doRecord(frame1,camera,start_milli,percentage,id,"sensor")
                record_timer = 0
                counter += 1
                record_lock = True
                id += 1
            else:
                if(record_timer==120):
                    print("\n==> Auto Recording")
                    doRecord(frame1,camera,start_milli,percentage,id,"auto")
                    record_timer = 0
                    counter += 1
                    record_lock = True
                    id += 1
                else:
                    record_timer += 1
                    print(f"====> Auto Record in {120-record_timer}s",end="\r")
                    time.sleep(1)

    print("\n==> Closing Camera",end="",flush=True)
    CameraHandler.closeCamera(camera)
    print(" > [DONE]")
    print("==> Detection Finished\n")

def doRecord(frame1,camera,start_milli,percentage,id,label):
    global ref,bucket,process,record_lock,counter,hash
    print(f"==> Recording Object {str(id).zfill(4)}",end="",flush=True)

    # Recording Parameters
    record_time = 0
    height = int(frame1.shape[0])
    width = int(frame1.shape[1])
    size = (width,height)
    filename = "Records/Record_"+str(datetime.now().strftime("%d-%m-%Y_%H.%M.%S"))+".avi"
    writeVid = cv2.VideoWriter(filename,cv2.VideoWriter_fourcc(*'MJPG'),5, size)

    # Recording Phase
    while(record_time<120):
        frame = CameraHandler.getFrame(camera)
        # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        writeVid.write(frame)
        record_time += 1
    writeVid.release()
    print(" > [DONE]")
    print("==> Loading Video",end="",flush=True)

    # Load Video
    in_video = open(filename, "rb")
    video_byte = in_video.read()
    in_video.close()
    # Remove Video
    if os.path.isfile(filename):
        os.remove(filename)
    print(" > [DONE]")

    # Blockchain
    print("==> Generating Blockchain",end="",flush=True)
    # Generate UUID
    identifier = Blockchain.getIdentifier()
    # Reset Blockchain Parameters
    data = {}
    telemetry = {}
    # Blockchain Data
    if(hash is None):
        previous = "None"
    else:
        previous = hash
    data.update({"0-0 Data":Blockchain.encryptMessage(identifier)})
    telemetry = setTelemetry(telemetry,start_milli,percentage,process,label)
    data.update({"0-1 Telemetry":telemetry})
    # Block Encapsulation
    block = Blockchain(previous,data)
    hash = Blockchain.getHash(block)
    block.setHash(hash)
    print(" > [DONE]")

    # Blockchain Query and Data Upload
    print(f"==> Uploading Data ({len(video_byte)})",end="",flush=True)
    FirebaseHandler.uploadData(bucket,video_byte,identifier)
    print(" > [SUCCESS]")
    print("==> Uploading Blockchain",end="",flush=True)
    FirebaseHandler.insertData(ref,id,block)
    print(" > [SUCCESS]")
    print(f"====> Block Uploaded\n")

def setTelemetry(telemetry,start_milli,percentage,process,label):
    # Telemetry - User
    user,uid,gid = Telemetry.getUserInfo()
    telemetry.update({"1-0 User":
                    {"1-1 Username":Blockchain.encryptMessage(user),
                    "1-2 UID":Blockchain.encryptMessage(uid),
                    "1-3 GID":Blockchain.encryptMessage(gid)
                    }})

    # Telemetry - Machine
    system,release,machine,arch,kernel = Telemetry.getMachineInfo()
    telemetry.update({"2-0 Machine":
                    {"2-1 System":Blockchain.encryptMessage(system),
                    "2-2 Release":Blockchain.encryptMessage(release),
                    "2-3 Machine":Blockchain.encryptMessage(machine),
                    "2-4 Architecture":Blockchain.encryptMessage(arch),
                    "2-5 Kernel":Blockchain.encryptMessage(kernel)
                    }})

    # Telemetry - Benchmark
    cpu_percent,memory_percent,text_usage,data_usage,cpu_temp = Telemetry.getBenchmarkInfo(process)
    end_milli = current_milli_time()
    time_milli = end_milli - start_milli
    telemetry.update({"3-0 Benchmark":
                    {"3-1 CPU Percent":Blockchain.encryptMessage(cpu_percent),
                    "3-2 Memory Percent":Blockchain.encryptMessage(memory_percent),
                    "3-3 Text Usage":Blockchain.encryptMessage(text_usage),
                    "3-4 Data Usage":Blockchain.encryptMessage(data_usage),
                    "3-5 CPU Temp":Blockchain.encryptMessage(cpu_temp),
                    "3-6 Time Milli":Blockchain.encryptMessage(str(time_milli)),
                    "3-7 Difference":Blockchain.encryptMessage(str(percentage)),
                    "3-8 Mode":Blockchain.encryptMessage(str(label))
                    }})

    # Telemetry - Network
    interface,ipaddr = Telemetry.getNetworkInfo()
    telemetry.update({"4-0 Network":
                    {"4-1 Interface":Blockchain.encryptMessage(interface),
                    "4-2 IP Address":Blockchain.encryptMessage(ipaddr)
                    }})

    # Telemetry - Date Time
    day,date,timenow,tzname = Telemetry.getDateTimeInfo()
    telemetry.update({"5-0 Datetime":
                    {"5-1 Day":Blockchain.encryptMessage(day),
                    "5-2 Date":Blockchain.encryptMessage(date),
                    "5-3 Time":Blockchain.encryptMessage(timenow),
                    "5-4 Timezone":Blockchain.encryptMessage(tzname)
                    }})
    return telemetry

def current_milli_time():
    return round(time.time() * 1000)

def verifyKeys():
    print("==> Checking Keys",end="",flush=True)
    pubkeypem = os.path.exists("keys/pubkey.pem")
    privkeypem = os.path.exists("keys/privkey.pem")
    if(pubkeypem == True and privkeypem == True):
        print(" > [FOUND]")
        return True
    else:
        print(" > [NOT FOUND]")
        return False

def main():
    global ref,bucket,process,record_lock,counter
    print("Blockchain Motion Detection")
    keys  = verifyKeys()
    if(keys == True):
        print("==> Connecting to Firebase",end="",flush=True)
        ref = FirebaseHandler.connectDB() # Connect Firebase
        print(" > [CONNECTED]")
        print("==> Connecting to Google Storage",end="",flush=True)
        bucket = FirebaseHandler.connectBucket() # Connect Google Storage
        print(" > [CONNECTED]")
        print("==> Starting Benchmark Function",end="",flush=True)
        process = Telemetry.getProcess()
        print(" > [DONE]")
        runDetection()
    else:
        print("==> Detection Aborted\n")

if __name__ == '__main__':
    main()
