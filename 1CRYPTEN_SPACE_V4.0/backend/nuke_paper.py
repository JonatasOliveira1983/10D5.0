import asyncio, sys; sys.path.insert(0, '.'); from services.sovereign_service import sovereign_service; asyncio.run(sovereign_service.db.collection('paper_state').document('current').delete())
