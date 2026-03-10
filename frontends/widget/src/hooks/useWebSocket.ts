/**
 * useWebSocket Hook — WebSocket-Verbindung mit automatischem Reconnect.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface UseWebSocketOptions {
  url: string;
  studio: string;
  visitorId: string;
  onMessage?: (message: Message) => void;
}

interface UseWebSocketReturn {
  messages: Message[];
  send: (text: string) => void;
  connected: boolean;
  connecting: boolean;
}

export function useWebSocket({
  url,
  studio,
  visitorId,
  onMessage,
}: UseWebSocketOptions): UseWebSocketReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnecting(true);
    const wsUrl = `${url}/ws/chat?studio=${studio}&visitor=${visitorId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setConnecting(false);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data as string);
        if (data.type === 'message') {
          const msg: Message = {
            role: data.role,
            content: data.content,
            timestamp: data.timestamp ?? new Date().toISOString(),
          };
          setMessages((prev) => [...prev, msg]);
          onMessage?.(msg);
        }
      } catch {
        // Nicht-JSON Nachricht ignorieren
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setConnecting(false);
      // Reconnect nach 3 Sekunden
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [url, studio, visitorId, onMessage]);

  useEffect(() => {
    connect();
    return () => {
      reconnectTimeoutRef.current && clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message: text }));
    }
  }, []);

  return { messages, send, connected, connecting };
}
