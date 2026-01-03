import { useGameState } from './hooks/useGameState';
import { Lobby } from './components/Lobby';
import { GameBoard } from './components/GameBoard';

function App() {
  const {
    gameState,
    isLoading,
    error,
    createGame,
    startGame,
    advancePhase,
  } = useGameState();

  const handlePlayAgain = () => {
    window.location.reload();
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-[var(--bg-card)] rounded-xl p-8 text-center">
          <h2 className="text-xl font-bold text-[var(--failure)] mb-4">Error</h2>
          <p className="text-[var(--text-secondary)] mb-4">{error}</p>
          <button
            onClick={handlePlayAgain}
            className="bg-[var(--player-1)] hover:bg-[var(--player-1)]/80 text-white font-bold py-2 px-6 rounded-lg"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!gameState || gameState.status === 'lobby') {
    return (
      <Lobby
        onCreateGame={createGame}
        onStartGame={startGame}
        gameId={gameState?.gameId || null}
        isLoading={isLoading}
      />
    );
  }

  return (
    <GameBoard
      gameState={gameState}
      isLoading={isLoading}
      onAdvancePhase={advancePhase}
      onPlayAgain={handlePlayAgain}
    />
  );
}

export default App;
