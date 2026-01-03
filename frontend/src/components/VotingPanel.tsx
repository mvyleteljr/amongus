import type { Vote } from '../types/game';

interface VotingPanelProps {
  votes: Vote[];
  suspectVotes: Record<number, number>;
  chosenSubmission: number | null;
}

const PLAYER_COLORS = [
  'text-[#58a6ff]',
  'text-[#3fb950]',
  'text-[#d29922]',
  'text-[#f778ba]',
];

export function VotingPanel({ votes, suspectVotes, chosenSubmission }: VotingPanelProps) {
  if (votes.length === 0) {
    return (
      <div className="rounded-lg bg-[var(--bg-card)] p-4">
        <h3 className="text-lg font-bold mb-4">Votes</h3>
        <div className="text-[var(--text-secondary)]">
          Waiting for votes...
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-[var(--bg-card)] p-4">
      <h3 className="text-lg font-bold mb-4">Votes</h3>
      
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
          Solution Votes
        </h4>
        <div className="space-y-1">
          {votes.map((vote) => (
            <div key={vote.voterIndex} className="text-sm">
              <span className={PLAYER_COLORS[vote.voterIndex]}>
                P{vote.voterIndex + 1}
              </span>
              <span className="text-[var(--text-secondary)]"> voted for </span>
              <span className={PLAYER_COLORS[vote.solutionVote]}>
                P{vote.solutionVote + 1}'s solution
              </span>
            </div>
          ))}
        </div>
        {chosenSubmission !== null && (
          <div className="mt-2 text-sm font-semibold text-[var(--success)]">
            Chosen: Player {chosenSubmission + 1}'s solution
          </div>
        )}
      </div>

      <div>
        <h4 className="text-sm font-semibold text-[var(--text-secondary)] mb-2">
          Suspect Votes
        </h4>
        <div className="space-y-1">
          {votes.map((vote) => (
            <div key={vote.voterIndex} className="text-sm">
              <span className={PLAYER_COLORS[vote.voterIndex]}>
                P{vote.voterIndex + 1}
              </span>
              <span className="text-[var(--text-secondary)]"> suspects </span>
              <span className={PLAYER_COLORS[vote.suspectVote]}>
                P{vote.suspectVote + 1}
              </span>
            </div>
          ))}
        </div>
        <div className="mt-2 text-sm">
          <span className="text-[var(--text-secondary)]">Tally: </span>
          {Object.entries(suspectVotes)
            .sort(([, a], [, b]) => b - a)
            .map(([playerIdx, count]) => (
              <span key={playerIdx} className="mr-3">
                <span className={PLAYER_COLORS[parseInt(playerIdx)]}>
                  P{parseInt(playerIdx) + 1}
                </span>
                : {count}
              </span>
            ))}
        </div>
      </div>
    </div>
  );
}
