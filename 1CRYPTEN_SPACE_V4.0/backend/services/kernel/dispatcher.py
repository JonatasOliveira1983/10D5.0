import logging
import asyncio
from typing import Dict, Any, List, Optional
from services.agents.aios_adapter import AIOSAgent
from services.kernel.scheduler import scheduler, Priority

logger = logging.getLogger("Dispatcher")

class AIOSKernel:
    """
    Pythonic AIOS Kernel (The Dispatcher).
    Orchestrates specialized agents and manages shared system context.
    Now with Priority Scheduling (V17.0).
    """
    
    # Priority mapping by role
    PRIORITY_MAP = {
        "Sentinel": Priority.URGENT,
        "Captain": Priority.HIGH,
        "Chronicler": Priority.BACKGROUND
    }
    
    def __init__(self):
        self.agents: Dict[str, AIOSAgent] = {}
        self.roles: Dict[str, str] = {} # role -> agent_id mapping
        self.session_context: Dict[str, Any] = {}
        
    async def register_agent(self, agent: AIOSAgent):
        """Registers an agent with the kernel."""
        manifest = await agent.handshake()
        agent_id = manifest["agent_id"]
        role = manifest["role"]
        
        self.agents[agent_id] = agent
        self.roles[role] = agent_id
        
        logger.info(f"🦾 [KERNEL] Agent Registered: {role} (ID: {agent_id}) | Caps: {manifest['capabilities']}")

    async def dispatch(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Routes a message to the target agent through the Priority Scheduler.
        """
        receiver = message.get("receiver")
        sender = message.get("sender")
        
        # Resolve role to agent_id
        target_id = self.roles.get(receiver) if receiver in self.roles else receiver
        
        if target_id not in self.agents:
            logger.error(f"❌ [KERNEL] Message drop: Target {receiver} unknown.")
            return None
            
        # Determine priority based on role or sender
        priority = self.PRIORITY_MAP.get(receiver, Priority.NORMAL)
        if sender == "Sentinel": # Explicit boost for sentinel requests
            priority = Priority.URGENT

        logger.debug(f"📨 [KERNEL] Scheduling: {sender} -> {receiver} ({message['type']}) | Priority: {priority.name}")
        
        try:
            # 🚦 Wait for the scheduler to allow execution
            await scheduler.schedule(message, priority=priority)
            
            # Execute the message
            response = await self.agents[target_id].on_message(message)
            return response
        except Exception as e:
            logger.error(f"❌ [KERNEL] Scheduler/Agent Error ({receiver}): {e}")
            return {"status": "error", "message": str(e)}

    def get_agent_by_role(self, role: str) -> Optional[AIOSAgent]:
        agent_id = self.roles.get(role)
        return self.agents.get(agent_id) if agent_id else None

# Singleton Kernel instance
kernel = AIOSKernel()

