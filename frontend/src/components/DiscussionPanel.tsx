import type { Message } from '../types/game';

interface DiscussionPanelProps {
  messages: Message[];
  currentDiscussionRound: number;
}

const PLAYER_COLORS = [
  'text-[#58a6ff]',
  'text-[#3fb950]',
  'text-[#d29922]',
  'text-[#f778ba]',
];

const PLAYER_BG_COLORS = [
  'bg-[#58a6ff]/10 border-[#58a6ff]/30',
  'bg-[#3fb950]/10 border-[#3fb950]/30',
  'bg-[#d29922]/10 border-[#d29922]/30',
  'bg-[#f778ba]/10 border-[#f778ba]/30',
];

export function DiscussionPanel({ messages, currentDiscussionRound }: DiscussionPanelProps) {
  if (messages.length === 0) {
    return (
      <div className="rounded-lg bg-[var(--bg-card)] p-4 h-full">
        <h3 className="text-lg font-bold mb-4">Discussion</h3>
        <div className="text-[var(--text-secondary)]">
          Discussion will begin after code reveal...
        </div>
      </div>
    );
  }

  const groupedByRound: Record<number, Message[]> = {};
  messages.forEach(msg => {
    if (!groupedByRound[msg.discussionRound]) {
      groupedByRound[msg.discussionRound] = [];
    }
    groupedByRound[msg.discussionRound].push(msg);
  });

  return (
    <div className="rounded-lg bg-[var(--bg-card)] p-4 h-full overflow-y-auto">
      <h3 className="text-lg font-bold mb-4">
        Discussion (Round {currentDiscussionRound}/3)
      </h3>
      <div className="space-y-4">
        {Object.entries(groupedByRound).map(([round, msgs]) => (
          <div key={round}>
            <div className="text-xs text-[var(--text-secondary)] mb-2">
              Round {round}
            </div>
            <div className="space-y-2">
              {msgs.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border ${PLAYER_BG_COLORS[msg.playerIndex]}`}
                >
                  <div className={`font-semibold text-sm ${PLAYER_COLORS[msg.playerIndex]}`}>
                    Player {msg.playerIndex + 1}
                  </div>
                  <div className="text-sm mt-1 text-[var(--text-primary)]">
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
