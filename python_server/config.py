import os

class Config:
    # Server
    HOST = "0.0.0.0"
    PORT = 8080

    # APNs
    APNS_TOPIC = "me.fin.bark"
    APNS_KEY_ID = "LH4T9V5U4R"
    APNS_TEAM_ID = "5U8LBRXG3A"
    
    # Path references
    SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(SERVER_DIR, ".."))
    
    APNS_KEY_PATH = os.path.join(SERVER_DIR, "AuthKey_LH4T9V5U4R_5U8LBRXG3A.p8")
    
    # Database
    DATABASE_URL = "sqlite:///./bark.db"
