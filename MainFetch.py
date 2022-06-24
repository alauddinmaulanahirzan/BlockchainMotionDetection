# Firebase Section
from FirebaseHandler import FirebaseHandler
# Blockchain Section
from Blockchain import Blockchain
# Telegram Bot Section
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# Additional Section
import os
from datetime import datetime
import csv
import time

# Logging Config
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hyper Parameters
ref = None
bucket = None

# Millis
def current_milli_time():
    return round(time.time() * 1000)

# --- Firebase Code --- #
def connectFirebase():
    print("==> Connecting to Firebase",end="",flush=True)
    ref = FirebaseHandler.connectDB() # Connect Once
    print(" > [CONNECTED]")
    print("==> Connecting to Google Storage",end="",flush=True)
    bucket = FirebaseHandler.connectBucket() # Connect Google Storage
    print(" > [CONNECTED]")
    return ref,bucket

# --- Telegram Bot Code --- #
def start(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = ">> ======================\n"
    message += ">> Bot : Motion Detection Bot Ready\n"
    message += ">> Bot : Available Commands:\n"
    message += ">> ======================\n"
    message += "1. /all_machines | Display All Machines\n"
    message += "2. /all_blocks | Display All Blocks\n"
    message += "3. /all_data | Display The Size of The Data\n"
    message += ">> ======================\n"
    message += "4. /latest | Display The Latest Blocks (<60 mins)\n"
    message += "5. /mode | List All Blocks Sorted by mode\n"
    message += ">> ======================\n"
    message += "6. /verify_blocks | Verify Blockchain Validity\n"
    message += "7. /verify_key | Verify Encryption Key\n"
    message += "8. /verify_data | Verify Data\n"
    message += ">> ======================\n"
    message += "9. /block | Display All Blocks in A Machine\n"
    message += "10. /data | Fetch Data From A Block\n"
    message += ">> ======================\n"
    message += "11. /benchmark | Retrieve Telemetries\n"
    message += ">> ======================\n"
    end_mil = current_milli_time()
    message += f">> Bot : Finished ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyKeys(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Memeriksa kunci kriptografi"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    pubkeypem = os.path.exists("keys/pubkey.pem")
    privkeypem = os.path.exists("keys/privkey.pem")
    if(pubkeypem == True and privkeypem == True):
        message = f">> Bot : Kunci ditemukan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Kunci tidak ditemukan\n"
        message += f">> Bot : Jalankan 'pyton3 RSAKeygen.py'\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyBlocks(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Verifying Blockchain Validity"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    total_blocks = 0
    invalid_blocks = []
    valid = 0
    invalid = 0
    curHash = None
    # Fetch Machine
    db = ref.get()
    if(db is not None):
        # Iterate per Machine
        for machine in db.keys():
            blocks = ref.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                total_blocks += 1
                block_data = ref.child(machine).child(block).get()
                if(block_data["01 Previous"] == "None" and block == "B_0001"):
                    valid += 1
                else:
                    if(curHash == block_data["01 Previous"]):
                        valid += 1
                    else:
                        invalid += 1
                        invalid_blocks.append(machine+":"+block)
                curHash = block_data["03 Hash"]

        message = f">> Bot : Found {total_blocks} blocks\n"
        message += f"==>> Valid Blocks : {valid}\n"
        message += f"==>> Invalid Blocks : {invalid}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        message = "==>> List of Blocks :\n"
        for list in invalid_blocks:
            message += f"====>> {list}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Nothing Found"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Finished ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botVerifyData(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Memeriksa validitas Data"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    # Fetch Machine
    db = ref.get()
    if(db is not None):
        # Iterate per Machine
        for machine in db.keys():
            total_data = 0
            missing = []
            data_exist = 0
            data_missing = 0
            message = f">> Bot : Memeriksa data di mesin '{machine}' (Tunggu)"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            blocks = ref.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                total_data += 1
                block_data = ref.child(machine).child(block).get()
                video_id = block_data['02 Data']['0-0 Data']
                # Check Data
                status = FirebaseHandler.checkData(bucket,Blockchain.decryptMessage(str(video_id)))
                if(status == True):
                    data_exist += 1
                else:
                    data_missing += 1
                    missing.append(machine+":"+block)
            message = f">> Bot : Menemukan {total_data} data di '{machine}'\n"
            message += f"==>> Data ada : {data_exist}\n"
            message += f"==>> Data hilang : {data_missing}\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            message = "==>> Daftar data :\n"
            for list in missing:
                message += f"====>> {missing}\n"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetDataSize(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Mengukur jumlah data tersimpan"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    total_size = 0
    # Fetch Machine
    db = ref.get()
    if(db is not None):
        machine_size = 0
        # Iterate per Machine
        for machine in db.keys():
            message = f">> Bot : Memeriksa jumlah data di mesin '{machine}' (Tunggu)"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            blocks = ref.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                block_data = ref.child(machine).child(block).get()
                video_id = block_data['02 Data']['0-0 Data']
                # Check Data
                video_id = Blockchain.decryptMessage(str(video_id))
                size = FirebaseHandler.getDataSize(bucket,video_id)
                machine_size += size
                print(f"==> Obtaining : {machine_size} current",end="\r")
            total_size += machine_size
            machine_size = machine_size/(1024*1024)
            message = ">> Bot : Menemukan %.3f MB\n"%machine_size
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        total_size = total_size/(1024*1024)
        message = ">> Bot : Menemukan total data %.3f MB keseluruhan \n"%total_size
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetAllMachines(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    machines = []
    counter = 1
    message = ">> Bot : Mengambil mesin dari DB"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    db = ref.get()
    if(db is not None):
        # Iterate per machine
        for machine in db.keys():   # By Machine
            machines.append(machine)
        message = f">> Bot : Menemukan {len(machines)} mesin\n"
        for machine in machines:
            message += f"==>> {counter}. {machine}\n"
            counter += 1
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetAllBlocks(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Mengambil semua blok di DB"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    total = 0
    db = ref.get()
    if(db is not None):
        for machine in db.keys():
            counter = 0
            message = f"==>> '{machine}' : "
            blocks = ref.child(machine).get()
            for block in blocks.keys():
                counter += 1
            message += f"{counter} blok\n"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            total += counter
        message = f"==>> Total blok : {total} blok\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetBlocks(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    args_len = len(context.args)
    args = context.args
    blocks_id = []
    if(args_len == 0):
        message = f">> Bot : Format Perintah /blok [nama mesin]"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    elif(args_len>1):
        message = f">> Bot : Memerlukan 1 argumen, {args_len} ditemukan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        if(args[0].isnumeric()):
            message = f">> Bot : Memerlukan teks sebagai argumen"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            machine = args[0]
            message = f">> Bot : Mengambil blok dari mesin '{machine}'"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            db = ref.child(machine).get()
            if(db is not None):
                message = f"==>> '{machine}' : "
                for block in db.keys():
                    blocks_id.append(block)
                message = f"====>> Blok '{blocks_id[0]}' <-> '{blocks_id[len(blocks_id)-1]}'"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            else:
                message = f">> Bot : Tidak menemukan apapun"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetData(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    args_len = len(context.args)
    args = context.args
    if(args_len == 0):
        message = f">> Bot : Format Perintah /data [nama mesin] [nama blok]"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    elif(args_len>2 or args_len==1):
        message = f">> Bot : Memerlukan 2 argumen, {args_len} ditemukan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        if(args[0].isnumeric() or args[1].isnumeric()):
            message = f">> Bot : Memerlukan teks sebagai argumen"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            machine = args[0]
            block = args[1]
            message = f">> Bot : Fetching Data From '{block}' in '{machine}'"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            db = ref.child(machine).child(block).get()
            if(db is not None):
                # Retrieve Data
                video_id = db['02 Data']['0-0 Data']
                # Download Data
                message = f">> Bot : Downloading Data From '{block}' (Please Wait)"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                video_data,status = FirebaseHandler.downloadData(bucket,Blockchain.decryptMessage(str(video_id)))
                # Sending Video
                message = f">> Bot : Sending Data to User (Please Wait)"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                # Get Date Time
                block_telemetry = db['02 Data']['0-1 Telemetry']
                block_datetime = block_telemetry['5-0 Datetime']
                block_date = block_datetime['5-2 Date']
                block_time = block_datetime['5-3 Time']
                block_date = Blockchain.decryptMessage(block_date)
                block_time = Blockchain.decryptMessage(block_time)
                message = f"==>> Video '{block}' at {block_time} {block_date}"
                context.bot.send_video(chat_id=update.effective_chat.id, video=video_data, supports_streaming=False, timeout=1000)
            else:
                message = f">> Bot : Tidak menemukan data di blok {block} - mesin '{machine}'"
                context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Finished ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetRangeData(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    args_len = len(context.args)
    args = context.args
    list_blocks = []
    if(args_len == 0):
        message = f">> Bot : Format Perintah /data_jangkauan [nama mesin] [blok awal] [blok akhir]"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    elif(args_len>3 or args_len<=2):
        message = f">> Bot : Memerlukan 3 argumen, {args_len} ditemukan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        if(args[0].isnumeric() or args[1].isalpha() or args[2].isalpha()):
            message = f">> Bot : Memerlukan argumen 1 (teks), argumen 2 dan 3 (numerik)"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            machine = args[0]
            start = int(args[1])
            end = int(args[2])
            message = f">> Bot : Mengambil data di mesin '{machine}'"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            for i in range(start,end):
                block = "B_"+str(i).zfill(4)
                db = ref.child(machine).child(block).get()
                if(db is not None):
                    # Retrieve Data
                    video_id = db['02 Data']['0-0 Data']
                    video_id = Blockchain.decryptMessage(str(video_id))
                    # Sending Video
                    list_blocks.append(video_id)
                else:
                    message = f">> Bot : Tidak menemukan data di blok {block} - mesin '{machine}'"
                    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            message = f" List : {list_blocks}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetRecentBlocks(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    date = datetime.now().strftime("%d-%B-%Y")
    time = datetime.now().strftime("%H.%M.%S.%f")
    message = f">> Bot : Memerika blok 60 menit terakhir\n"
    message += f">> Bot : per tanggal '{date}' \n dan waktu '{time}'\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    old_blocks = 0
    new_blocks = 0
    db = ref.get()
    # Iterate per Machine
    if(db is not None):
        counter = 1
        for machine in db.keys():
            blocks = ref.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                block_data = ref.child(machine).child(block).get()
                # Get Telemetry and Datetime
                block_telemetry = block_data['02 Data']['0-1 Telemetry']
                block_datetime = block_telemetry['5-0 Datetime']
                block_date = block_datetime['5-2 Date']
                block_time = block_datetime['5-3 Time']
                # Get Mode
                block_benchmark = block_telemetry['3-0 Benchmark']
                block_benchmark_mode = block_benchmark['3-8 Mode']
                # Decrypt Data and Set Datetime
                block_date = Blockchain.decryptMessage(block_date)
                block_time = Blockchain.decryptMessage(block_time)
                block_mode = Blockchain.decryptMessage(block_benchmark_mode)
                block_datetime = block_date + " " +block_time
                block_datetime = datetime.strptime(block_datetime,"%d-%B-%Y %H.%M.%S.%f")
                # Get Current Date Time
                current_datetime = datetime.now()
                # Delta Time Block Age <= 60 Mins
                delta_mins = int((current_datetime-block_datetime).seconds/60)
                if(delta_mins<=60):
                    new_blocks += 1
                    counter += 1
                else:
                    old_blocks += 1
        message = f">> Bot : Menemukan {new_blocks+old_blocks} blok\n"
        message += f"====> Blok Lama : {old_blocks}\n"
        message += f"====> Blok Baru : {new_blocks}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGetMode(update: Update, context: CallbackContext) -> None:
    start_mil = current_milli_time()
    message = f">> Bot : Mengambil blok berdasarkan mode\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    auto_blocks = 0
    sensor_blocks = 0
    list_auto = []
    list_sensor = []
    counter = 1
    db = ref.get()
    if(db is not None):
        # Iterate per Machine
        for machine in db.keys():
            blocks = ref.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                block_data = ref.child(machine).child(block).get()
                # Get Telemetry
                block_telemetry = block_data['02 Data']['0-1 Telemetry']
                # Get Datetime
                block_datetime = block_telemetry['5-0 Datetime']
                block_date = block_datetime['5-2 Date']
                block_time = block_datetime['5-3 Time']
                # Get Mode
                block_benchmark = block_telemetry['3-0 Benchmark']
                block_benchmark_mode = block_benchmark['3-8 Mode']
                # Decrypt
                block_date = Blockchain.decryptMessage(block_date)
                block_time = Blockchain.decryptMessage(block_time)
                block_mode = Blockchain.decryptMessage(block_benchmark_mode)
                block_datetime = block_date + " " +block_time
                if(block_mode=="auto"):
                    auto_blocks+=1
                    list_auto.append(f"{machine} - {block} ({block_mode[0]}) : {block_datetime}")
                elif(block_mode=="sensor"):
                    sensor_blocks+=1
                    list_sensor.append(f"{machine} - {block} ({block_mode[0]}) : {block_datetime}")
        message = f">> Bot : Menemukan {auto_blocks+sensor_blocks} blok\n"
        message += f"==>> Blok Auto : {auto_blocks}\n"
        message += f"==>> Blok Sensor : {sensor_blocks}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def botGenerateBenchmark(update: Update, context: CallbackContext) -> None:
    counter = 1
    start_mil = current_milli_time()
    message = f">> Bot: Membuat file benchmark csv"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    db = ref.get()
    if(db is not None):
        data_rows = []
        # Iterate per Machine
        for machine in db.keys():
            message = f">> Bot : Mengambil Telemetry di '{machine}'"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            blocks = ref.child(machine).get()
            # Iterate per Block
            for block in blocks.keys():
                block_data = ref.child(machine).child(block).get()
                # Get Telemetry
                block_telemetry = block_data['02 Data']['0-1 Telemetry']
                # Get Timestamp
                block_datetime = block_telemetry['5-0 Datetime']
                block_date = block_datetime['5-2 Date']
                block_time = block_datetime['5-3 Time']
                # Decrypt Data and Set Datetime
                block_date = Blockchain.decryptMessage(block_date)
                block_time = Blockchain.decryptMessage(block_time)
                block_datetime = block_date + " " +block_time
                block_datetime = datetime.strptime(block_datetime,"%d-%B-%Y %H.%M.%S.%f")
                benchmark_timestamp = block_datetime.timestamp()*1000
                # Telemetry Section
                block_benchmark = block_telemetry['3-0 Benchmark']
                block_benchmark_cpu = block_benchmark['3-1 CPU Percent']
                block_benchmark_memory = block_benchmark['3-2 Memory Percent']
                block_benchmark_text = block_benchmark['3-3 Text Usage']
                block_benchmark_data = block_benchmark['3-4 Data Usage']
                block_benchmark_temp = block_benchmark['3-5 CPU Temp']
                block_benchmark_millis = block_benchmark['3-6 Time Milli']
                block_benchmark_diff = block_benchmark['3-7 Difference']
                block_benchmark_mode = block_benchmark['3-8 Mode']
                # Decrypt Data
                benchmark_cpu = Blockchain.decryptMessage(block_benchmark_cpu)
                benchmark_memory = Blockchain.decryptMessage(block_benchmark_memory)
                benchmark_text = Blockchain.decryptMessage(block_benchmark_text)
                benchmark_data = Blockchain.decryptMessage(block_benchmark_data)
                benchmark_temp = Blockchain.decryptMessage(block_benchmark_temp)
                benchmark_millis = Blockchain.decryptMessage(block_benchmark_millis)
                benchmark_diff = Blockchain.decryptMessage(block_benchmark_diff)
                benchmark_mode = Blockchain.decryptMessage(block_benchmark_mode)
                # Insert into Row
                row = []
                row.append(counter)
                row.append(machine)
                row.append(block)
                row.append(benchmark_timestamp)
                row.append(benchmark_cpu)
                row.append(benchmark_memory)
                row.append(benchmark_text)
                row.append(benchmark_data)
                row.append(benchmark_temp)
                row.append(benchmark_millis)
                row.append(benchmark_diff)
                row.append(benchmark_mode)
                data_rows.append(row)
                counter += 1

        # Write to CSV
        message = f">> Bot : Menyimpan data Telemetry di file"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        filename = "benchmark.csv"
        if os.path.isfile(filename):
            os.remove(filename)
        # Set Header CSV
        header = ["No","Machine","Block","Timestamp","CPU","Memory","Text","Data","Temp","Estimate","Diff","Label"]
        with open(filename,"w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for input_row in data_rows:
                writer.writerow(input_row)
        message = f">> Bot : File Telemetry sudah tersimpan"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = f">> Bot : Tidak menemukan apapun"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    end_mil = current_milli_time()
    message = f">> Bot : Selesai ({(end_mil-start_mil)/1000}s)"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# --- Main Code --- #
def main():
    global ref,bucket
    ref,bucket = connectFirebase()
    updater = Updater(token="1901469256:AAHz0864vwPsAS6HWu68GZ4uoQ8k_FS0YU8",request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})
    dispatcher = updater.dispatcher
    jq = updater.job_queue
    # Perintah
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("verify_keys", botVerifyKeys))
    dispatcher.add_handler(CommandHandler("verify_blocks", botVerifyBlocks))
    dispatcher.add_handler(CommandHandler("verify_data", botVerifyData))
    dispatcher.add_handler(CommandHandler("all_machines", botGetAllMachines))
    dispatcher.add_handler(CommandHandler("all_blocks", botGetAllBlocks))
    dispatcher.add_handler(CommandHandler("all_data", botGetDataSize))
    dispatcher.add_handler(CommandHandler("block", botGetBlocks))
    dispatcher.add_handler(CommandHandler("data", botGetData))
    dispatcher.add_handler(CommandHandler("data_jangkauan", botGetRangeData))
    dispatcher.add_handler(CommandHandler("latest", botGetRecentBlocks))
    dispatcher.add_handler(CommandHandler("mode", botGetMode))
    dispatcher.add_handler(CommandHandler("benchmark", botGenerateBenchmark))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
