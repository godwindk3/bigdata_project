from dotenv import load_dotenv
load_dotenv()
import os



MONGO_URL=os.getenv('MONGO_URL')

print(MONGO_URL)

    


