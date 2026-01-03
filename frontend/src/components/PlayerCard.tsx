import type { Player } from '../types/game';

interface PlayerCardProps {
  player: Player;
  suspectVotes: number;
  hasSubmitted: boolean;
  isImposter?: boolean;
  isSelected?: boolean;
  onClick?: () => void;
  revealModel?: boolean;
}

const PLAYER_COLORS = [
  'border-[#58a6ff] bg-[#58a6ff]/10',
  'border-[#3fb950] bg-[#3fb950]/10',
  'border-[#d29922] bg-[#d29922]/10',
  'border-[#f778ba] bg-[#f778ba]/10',
];

const PLAYER_TEXT_COLORS = [
  'text-[#58a6ff]',
  'text-[#3fb950]',
  'text-[#d29922]',
  'text-[#f778ba]',
];

export function PlayerCard({
  player,
  suspectVotes,
  hasSubmitted,
  isImposter,
  isSelected,
  onClick,
  revealModel,
}: PlayerCardProps) {
  const colorClass = PLAYER_COLORS[player.index];
  const textColor = PLAYER_TEXT_COLORS[player.index];

  return (
    <div
      onClick={onClick}
      className={`
        rounded-lg border-2 p-4 transition-all
        ${colorClass}
        ${player.isEliminated ? 'opacity-50 grayscale' : ''}
        ${isSelected ? 'ring-2 ring-white' : ''}
        ${onClick ? 'cursor-pointer hover:scale-105' : ''}
      `}
    >
      <div className={`text-lg font-bold ${textColor}`}>
        {player.name}
        {isImposter && <span className="ml-2 text-red-500">(Imposter)</span>}
      </div>
      <div className="text-sm text-[var(--text-secondary)]">
        {revealModel ? player.model.split('/').pop() : '???'}
      </div>
      <div className="mt-2 text-sm">
        {player.isEliminated ? (
          <span className="text-red-500">ELIMINATED</span>
        ) : hasSubmitted ? (
          <span className="text-green-500">Submitted</span>
        ) : (
          <span className="text-yellow-500">Thinking...</span>
        )}
      </div>
      {suspectVotes > 0 && !player.isEliminated && (
        <div className="mt-1 text-sm text-[var(--warning)]">
          Suspects: {suspectVotes}
        </div>
      )}
    </div>
  );
}
