# Firebase Section
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
from google.cloud import storage
# Additional Section
import platform

class FirebaseHandler:
    def connectDB():
        databaseURL = "https://iot-db-b4768-default-rtdb.asia-southeast1.firebasedatabase.app/"
        cred = credentials.Certificate("iot-db-adminsdk.json")
        app = firebase_admin.initialize_app(cred,{'databaseURL':databaseURL})
        reference = db.reference("/")
        return reference

    def insertData(ref,id,block):
        # Set Machine Key
        target_platform = platform.uname().node.lower()
        # Set Target Block ID
        target_blockid = "B_"+str(id).zfill(4)
        # Set Target Reference
        target_ref = ref.child(target_platform).child(target_blockid)
        # Insert
        target_ref.set({"01 Previous":block.previous,
                        "02 Data":block.data,
                        "03 Hash":block.hash})

    def connectBucket():
        storage_client = storage.Client.from_service_account_json('iot-db-adminsdk.json')
        bucket = storage_client.get_bucket("iot-db-b4768.appspot.com",timeout=None)
        return bucket

    def uploadData(bucket,byte_data,identifier):
        blob = bucket.blob(identifier)          # Identifier from UUID
        blob.upload_from_string(byte_data)      # Data in Byte
        if(blob.exists() == True):
            return True
        else:
            return False

    def downloadData(bucket,identifier):
        data = None
        blob = bucket.blob(identifier)         # Identifier from DB
        if(blob.exists() == True):
            blob.reload()
            data = blob.download_as_string()
            return data,True
        else:
            return data,False

    def checkData(bucket,identifier):
        blob = bucket.blob(identifier)       # Identifier from DB
        if(blob.exists() == True):
            return True
        else:
            return False

    def getDataSize(bucket,identifier):
        blob = bucket.blob(identifier)       # Identifier from DB
        if(blob.exists() == True):
            blob = bucket.get_blob(identifier)
            size = blob.size
            return size
        else:
            return 0
