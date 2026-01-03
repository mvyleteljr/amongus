import type { GameState } from '../types/game';
import { Header } from './Header';
import { PlayerCard } from './PlayerCard';
import { CodeViewer } from './CodeViewer';
import { DiscussionPanel } from './DiscussionPanel';
import { VotingPanel } from './VotingPanel';
import { TestResults } from './TestResults';
import { TaskProgress } from './TaskProgress';
import { GameOverModal } from './GameOverModal';

interface GameBoardProps {
  gameState: GameState;
  isLoading: boolean;
  onAdvancePhase: () => void;
  onPlayAgain: () => void;
}

export function GameBoard({ gameState, isLoading, onAdvancePhase, onPlayAgain }: GameBoardProps) {
  const currentRound = gameState.rounds[gameState.currentRound - 1];
  const submissions = currentRound?.submissions || [];
  const discussion = currentRound?.discussion || [];
  const votes = currentRound?.votes || [];
  const suspectVotes = currentRound?.suspectVotes || {};
  const testResults = currentRound?.testResults || null;
  const task = currentRound?.task;

  const getAdvanceButtonText = () => {
    if (isLoading) return 'Processing...';
    switch (gameState.currentPhase) {
      case 'coding': return 'Submit Code';
      case 'reveal': return 'Start Discussion';
      case 'discussion': return gameState.discussionRoundNumber >= 3 ? 'Start Voting' : 'Next Discussion Round';
      case 'voting': return 'Show Results';
      case 'results': return 'Next Round';
      default: return 'Advance';
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        currentRound={gameState.currentRound}
        currentPhase={gameState.currentPhase}
        discussionRound={gameState.discussionRoundNumber}
      />

      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {/* Player Cards */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {gameState.players.map((player) => (
            <PlayerCard
              key={player.index}
              player={player}
              suspectVotes={suspectVotes[player.index] || 0}
              hasSubmitted={submissions.some(s => s.playerIndex === player.index)}
              isImposter={gameState.status === 'finished' && player.index === gameState.imposterIndex}
              revealModel={gameState.status === 'finished'}
            />
          ))}
        </div>

        {/* Task Info */}
        {task && (
          <div className="bg-[var(--bg-card)] rounded-lg p-4 mb-6">
            <h2 className="text-xl font-bold mb-2">{task.title}</h2>
            <pre className="text-sm text-[var(--text-secondary)] whitespace-pre-wrap">
              {task.description}
            </pre>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="space-y-6">
            <CodeViewer
              submissions={submissions}
              chosenSubmission={currentRound?.chosenSubmission}
            />
            {testResults && <TestResults results={testResults} />}
          </div>
          <div className="space-y-6">
            <DiscussionPanel
              messages={discussion}
              currentDiscussionRound={gameState.discussionRoundNumber}
            />
            {votes.length > 0 && (
              <VotingPanel
                votes={votes}
                suspectVotes={suspectVotes}
                chosenSubmission={currentRound?.chosenSubmission ?? null}
              />
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between bg-[var(--bg-secondary)] rounded-lg p-4">
          <TaskProgress rounds={gameState.rounds} currentRound={gameState.currentRound} />
          
          {gameState.status === 'in_progress' && (
            <button
              onClick={onAdvancePhase}
              disabled={isLoading}
              className="bg-[var(--player-1)] hover:bg-[var(--player-1)]/80 disabled:opacity-50 text-white font-bold py-2 px-6 rounded-lg transition-colors"
            >
              {getAdvanceButtonText()}
            </button>
          )}
        </div>
      </main>

      {/* Game Over Modal */}
      {gameState.status === 'finished' && gameState.winner && (
        <GameOverModal gameState={gameState} onPlayAgain={onPlayAgain} />
      )}
    </div>
  );
}
