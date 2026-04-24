import os
import logging
import time
import shutil
import asyncio
from typing import List, Dict, Any
from services.agents.aios_adapter import AIOSAgent
from services.database_service import database_service

logger = logging.getLogger("GuardianAgent")

class GuardianAgent(AIOSAgent):
    """
    [V110.200] Infrastructure Specialist: The Custodian of 1CRYPTEN SPACE.
    Focuses on security, code integrity, and automated maintenance.
    """
    def __init__(self):
        super().__init__(
            agent_id="agent-guardian-system",
            role="guardian",
            capabilities=["security_monitoring", "code_hygiene", "db_integrity_checks"]
        )
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.archive_dir = os.path.join(self.base_dir, "legacy_archives")
        self.essential_files = [
            "main.py", "config.py", "manage.py", "Procfile", 
            "requirements.txt", "Dockerfile"
        ]

    async def on_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = message.get("type")
        
        if msg_type == "PERFORM_HYGIENE_SCAN":
            results = await self.perform_hygiene_scan()
            return {"status": "SUCCESS", "data": results}
            
        if msg_type == "CHECK_DB_INTEGRITY":
            return await self.check_db_integrity()
            
        return {"status": "ERROR", "message": f"Unknown message type: {msg_type}"}

    async def perform_hygiene_scan(self) -> Dict[str, Any]:
        """Identifies obsolete scripts and temporary files."""
        logger.info("🛡️ [GUARDIAN] Starting system hygiene scan...")
        
        scanned_files = []
        obsolete_candidates = []
        
        # Walk through backend to find .py files that are not core services
        backend_path = os.path.join(self.base_dir)
        for file in os.listdir(backend_path):
            if file.endswith(".py"):
                if file not in self.essential_files and not file.startswith("__"):
                    # Logic: If it starts with 'test_', 'check_', 'debug_', 'audit_' or 'reset_'
                    # and was modified more than 24h ago, it's a candidate for archiving.
                    file_path = os.path.join(backend_path, file)
                    mtime = os.path.getmtime(file_path)
                    if time.time() - mtime > 86400: # 24 hours
                        if any(file.startswith(prefix) for prefix in ["test_", "check_", "debug_", "audit_", "reset_", "diag_", "nuke_"]):
                            obsolete_candidates.append(file)
        
        return {
            "obsolete_count": len(obsolete_candidates),
            "candidates": obsolete_candidates,
            "status": "AWAITING_ARCHIVE_CONFIRMATION"
        }

    async def check_db_integrity(self) -> Dict[str, Any]:
        """Verifies if critical tables and connections are healthy."""
        try:
            # Simple check via DatabaseService
            if not database_service.is_active:
                await database_service.initialize()
            
            # Count active slots as a health indicator
            from sqlalchemy import select
            from services.database_service import Slot
            async with database_service.AsyncSessionLocal() as session:
                result = await session.execute(select(Slot))
                slots = result.scalars().all()
                
            return {
                "status": "HEALTHY",
                "db_active": True,
                "slots_in_db": len(slots)
            }
        except Exception as e:
            logger.error(f"🛡️ [GUARDIAN] DB Integrity Check Failed: {e}")
            return {"status": "UNHEALTHY", "error": str(e)}

    async def archive_obsolete_files(self, files: List[str]):
        """Moves identified files to the legacy_archives folder."""
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
            
        archived_count = 0
        for file in files:
            src = os.path.join(self.base_dir, file)
            dst = os.path.join(self.archive_dir, file)
            try:
                if os.path.exists(src):
                    shutil.move(src, dst)
                    archived_count += 1
            except Exception as e:
                logger.error(f"Error archiving {file}: {e}")
        
        logger.info(f"🛡️ [GUARDIAN] Archived {archived_count} files to /legacy_archives")
        return archived_count

# Instance
guardian_agent = GuardianAgent()
