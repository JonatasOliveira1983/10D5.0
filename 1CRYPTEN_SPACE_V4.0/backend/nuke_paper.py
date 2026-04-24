import asyncio, sys; sys.path.insert(0, '.'); from services.firebase_service import firebase_service; asyncio.run(firebase_service.db.collection('paper_state').document('current').delete())
