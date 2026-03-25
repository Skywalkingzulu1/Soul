import os
import shutil
import zipfile
import time
from datetime import datetime
from soul.core.logger import setup_logger
from soul.providers.impossible import ImpossibleCloudClient

logger = setup_logger(__name__)

class MemoryManager:
    """Manages memory persistence, deduplication, and cloud backups."""
    
    def __init__(self, chroma_path="./chroma_db_persist", db_path="./memory.db"):
        self.chroma_path = chroma_path
        self.db_path = db_path
        self.cloud = ImpossibleCloudClient()

    def deduplicate(self, content: str, collection) -> bool:
        """Check if identical content exists in the last 100 entries to prevent bloat."""
        if not collection:
            return False
            
        results = collection.query(
            query_texts=[content],
            n_results=1
        )
        
        if results['distances'] and results['distances'][0]:
            # If cosine distance is very low (e.g., < 0.05), it's a duplicate
            if results['distances'][0][0] < 0.05:
                return True
        return False

    def create_snapshot(self) -> str:
        """Zip the memory databases for backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"soul_brain_snapshot_{timestamp}.zip"
        
        logger.info(f"Creating brain snapshot: {zip_name}")
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Zip SQLite DB
            if os.path.exists(self.db_path):
                zipf.write(self.db_path)
            
            # Zip ChromaDB directory
            if os.path.exists(self.chroma_path):
                for root, dirs, files in os.walk(self.chroma_path):
                    for file in files:
                        zipf.write(
                            os.path.join(root, file),
                            os.path.relpath(os.path.join(root, file), os.path.join(self.chroma_path, '..'))
                        )
        
        return zip_name

    async def backup_to_cloud(self, bucket_name="andile-soul-backups"):
        """Perform snapshot and upload to Impossible Cloud."""
        zip_path = self.create_snapshot()
        
        logger.info(f"Uploading snapshot to Impossible Cloud: {bucket_name}")
        success = self.cloud.upload_file(zip_path, bucket_name)
        
        if success:
            logger.info("Cloud backup successful. Cleaning up local zip.")
            os.remove(zip_path)
        else:
            logger.error("Cloud backup failed.")
        
        return success
