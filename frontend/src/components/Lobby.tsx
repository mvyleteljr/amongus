interface LobbyProps {
  onCreateGame: () => void;
  onStartGame: () => void;
  gameId: string | null;
  isLoading: boolean;
}

export function Lobby({ onCreateGame, onStartGame, gameId, isLoading }: LobbyProps) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="bg-[var(--bg-card)] rounded-xl p-8 max-w-md w-full mx-4 text-center">
        <h1 className="text-4xl font-bold mb-2">LLM Among Us</h1>
        <p className="text-[var(--text-secondary)] mb-8">
          4 LLMs compete in programming tasks. One is an imposter trying to sabotage.
        </p>

        {!gameId ? (
          <button
            onClick={onCreateGame}
            disabled={isLoading}
            className="w-full bg-[var(--player-1)] hover:bg-[var(--player-1)]/80 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition-colors"
          >
            {isLoading ? 'Creating...' : 'Create Game'}
          </button>
        ) : (
          <div>
            <div className="mb-4 p-3 bg-[var(--bg-secondary)] rounded-lg">
              <div className="text-sm text-[var(--text-secondary)]">Game ID</div>
              <div className="font-mono text-lg">{gameId}</div>
            </div>
            <button
              onClick={onStartGame}
              disabled={isLoading}
              className="w-full bg-[var(--success)] hover:bg-[var(--success)]/80 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              {isLoading ? 'Starting...' : 'Start Game'}
            </button>
          </div>
        )}

        <div className="mt-8 text-left">
          <h3 className="font-semibold mb-2 text-[var(--text-secondary)]">How it works:</h3>
          <ul className="text-sm text-[var(--text-secondary)] space-y-1">
            <li>4 LLMs are assigned roles: 3 Crewmates, 1 Imposter</li>
            <li>Each round, they solve a coding task</li>
            <li>They discuss and vote on which solution to use</li>
            <li>The imposter tries to sabotage without getting caught</li>
            <li>Crewmates win by catching the imposter</li>
            <li>Imposter wins by surviving or failing 3 tasks</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
