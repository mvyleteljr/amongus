import type { GameState } from '../types/game';

interface GameOverModalProps {
  gameState: GameState;
  onPlayAgain: () => void;
}

export function GameOverModal({ gameState, onPlayAgain }: GameOverModalProps) {
  const isCrewmatesWin = gameState.winner === 'crewmates';
  const imposterPlayer = gameState.players[gameState.imposterIndex ?? 0];

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div className="bg-[var(--bg-card)] rounded-xl p-8 max-w-md w-full mx-4 text-center">
        <h2 className={`text-3xl font-bold mb-4 ${isCrewmatesWin ? 'text-[var(--success)]' : 'text-[var(--failure)]'}`}>
          {isCrewmatesWin ? 'Crewmates Win!' : 'Imposter Wins!'}
        </h2>
        
        <div className="mb-6">
          <div className="text-[var(--text-secondary)] mb-2">The Imposter was:</div>
          <div className="text-xl font-bold text-[var(--failure)]">
            {imposterPlayer?.name} ({imposterPlayer?.model.split('/').pop()})
          </div>
        </div>

        <div className="mb-6 text-left bg-[var(--bg-secondary)] rounded-lg p-4">
          <h3 className="font-semibold mb-2">Game Stats</h3>
          <div className="text-sm space-y-1 text-[var(--text-secondary)]">
            <div>Rounds played: {gameState.currentRound}</div>
            <div>Tasks failed: {gameState.failedTaskCount}</div>
            {gameState.eliminatedPlayer !== null && (
              <div>
                Eliminated: Player {gameState.eliminatedPlayer + 1}
                {gameState.eliminatedPlayer === gameState.imposterIndex && (
                  <span className="text-[var(--success)]"> (Imposter caught!)</span>
                )}
              </div>
            )}
          </div>
        </div>

        <button
          onClick={onPlayAgain}
          className="bg-[var(--player-1)] hover:bg-[var(--player-1)]/80 text-white font-bold py-3 px-6 rounded-lg transition-colors"
        >
          Play Again
        </button>
      </div>
    </div>
  );
}
