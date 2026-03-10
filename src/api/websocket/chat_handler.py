"""WebSocket Chat-Endpoint: Empfängt Nachrichten und leitet sie an den Agent weiter."""

import json
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.websocket.manager import manager
from src.db.database import AsyncSessionLocal
from src.db.models.conversation import Conversation
from src.db.models.studio import Studio

log = structlog.get_logger()


async def handle_chat(websocket: WebSocket, studio_slug: str, visitor_id: str) -> None:
    """
    WebSocket-Handler für den Chat-Endpoint.

    /ws/chat?studio={slug}&visitor={visitor_id}

    1. Studio anhand slug laden → Verbindung schließen wenn nicht gefunden
    2. Konversation finden oder erstellen (via visitor_id)
    3. Richtigen Agent für das Studio laden (vorerst Echo)
    4. Bei jeder Nachricht: agent.process_message() aufrufen
    5. Antwort über WebSocket zurücksenden
    6. Bei Disconnect: Verbindung trennen
    """
    await manager.connect(websocket, visitor_id)

    try:
        async with AsyncSessionLocal() as session:
            # Studio laden
            result = await session.execute(
                select(Studio).where(Studio.slug == studio_slug)
            )
            studio = result.scalar_one_or_none()

            if studio is None:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Studio '{studio_slug}' nicht gefunden",
                })
                await websocket.close(code=4004)
                return

            # Konversation finden oder erstellen
            conv_result = await session.execute(
                select(Conversation)
                .where(Conversation.studio_id == studio.id)
                .where(Conversation.visitor_id == visitor_id)
                .where(Conversation.status == "active")
            )
            conversation = conv_result.scalar_one_or_none()

            if conversation is None:
                conversation = Conversation(
                    studio_id=studio.id,
                    visitor_id=visitor_id,
                    channel="widget",
                    status="active",
                )
                session.add(conversation)
                await session.commit()
                await session.refresh(conversation)

            log.info(
                "ws.chat_started",
                studio=studio_slug,
                visitor=visitor_id,
                conversation_id=str(conversation.id),
            )

            # Nachrichten-Loop
            while True:
                data = await websocket.receive_text()

                try:
                    payload = json.loads(data)
                    message_text = payload.get("message", data)
                except json.JSONDecodeError:
                    message_text = data

                log.info("ws.message_received", visitor=visitor_id, text_len=len(message_text))

                # TODO: Hier kommt später der echte Agent-Aufruf
                # Vorerst: Echo-Antwort für Tests
                echo_response = (
                    f"[Echo] Du hast geschrieben: {message_text} "
                    f"(Studio: {studio.name}, Konversation: {conversation.id})"
                )

                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": echo_response,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

    except WebSocketDisconnect:
        manager.disconnect(visitor_id)
        log.info("ws.disconnected", visitor=visitor_id)
    except Exception as e:
        log.error("ws.error", visitor=visitor_id, error=str(e))
        manager.disconnect(visitor_id)
