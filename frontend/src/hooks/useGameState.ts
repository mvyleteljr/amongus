import { useState, useEffect, useCallback, useRef } from 'react';
import type { GameState } from '../types/game';

const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';

export function useGameState() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connectWebSocket = useCallback((gameId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`${WS_URL}/ws/${gameId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'game_state_update' && message.data) {
        setGameState(message.data);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = () => {
      setError('WebSocket connection failed');
      setIsConnected(false);
    };
  }, []);

  const createGame = useCallback(async (models?: string[]) => {
    setIsLoading(true);
    setError(null);
    try {
      // Only pass models if it's actually an array (not an event object)
      const modelsToSend = Array.isArray(models) ? models : undefined;
      const response = await fetch(`${API_URL}/api/game/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ models: modelsToSend }),
      });
      if (!response.ok) throw new Error('Failed to create game');
      const data = await response.json();
      setGameState(data);
      connectWebSocket(data.gameId);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [connectWebSocket]);

  const startGame = useCallback(async () => {
    if (!gameState) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/game/${gameState.gameId}/start`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to start game');
      const data = await response.json();
      setGameState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [gameState]);

  const advancePhase = useCallback(async () => {
    if (!gameState) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/game/${gameState.gameId}/advance`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to advance phase');
      const data = await response.json();
      setGameState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [gameState]);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    gameState,
    isConnected,
    isLoading,
    error,
    createGame,
    startGame,
    advancePhase,
  };
}
