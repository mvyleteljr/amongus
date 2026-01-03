import type { GamePhase } from '../types/game';

interface HeaderProps {
  currentRound: number;
  currentPhase: GamePhase;
  discussionRound?: number;
}

const PHASE_LABELS: Record<GamePhase, string> = {
  lobby: 'Lobby',
  coding: 'Coding',
  reveal: 'Code Reveal',
  discussion: 'Discussion',
  voting: 'Voting',
  results: 'Results',
  finished: 'Game Over',
};

export function Header({ currentRound, currentPhase, discussionRound }: HeaderProps) {
  const phaseLabel = currentPhase === 'discussion' && discussionRound
    ? `Discussion (${discussionRound}/3)`
    : PHASE_LABELS[currentPhase];

  return (
    <header className="bg-[var(--bg-secondary)] border-b border-[var(--border)] px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold">
          LLM Among Us
        </h1>
        <div className="flex items-center gap-6">
          <div className="text-[var(--text-secondary)]">
            Round <span className="text-[var(--text-primary)] font-bold">{currentRound}/5</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-[var(--bg-card)] border border-[var(--border)]">
            {phaseLabel}
          </div>
        </div>
      </div>
    </header>
  );
}
