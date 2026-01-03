import type { Round } from '../types/game';

interface TaskProgressProps {
  rounds: Round[];
  currentRound: number;
}

export function TaskProgress({ rounds, currentRound }: TaskProgressProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-[var(--text-secondary)]">Tasks:</span>
      {[1, 2, 3, 4, 5].map((roundNum) => {
        const round = rounds.find(r => r.roundNumber === roundNum);
        const testResults = round?.testResults;
        
        let statusClass = 'bg-[var(--bg-card)] border-[var(--border)]';
        let symbol = '';
        
        if (testResults) {
          if (testResults.passed) {
            statusClass = 'bg-[var(--success)]/20 border-[var(--success)]';
            symbol = '';
          } else {
            statusClass = 'bg-[var(--failure)]/20 border-[var(--failure)]';
            symbol = '';
          }
        } else if (roundNum === currentRound) {
          statusClass = 'bg-[var(--warning)]/20 border-[var(--warning)]';
        }
        
        return (
          <div
            key={roundNum}
            className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-bold ${statusClass}`}
            title={round?.task?.title || `Round ${roundNum}`}
          >
            {symbol || roundNum}
          </div>
        );
      })}
    </div>
  );
}
