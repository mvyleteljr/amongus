import { useState } from 'react';
import type { Submission } from '../types/game';

interface CodeViewerProps {
  submissions: Submission[];
  chosenSubmission?: number | null;
}

const TAB_COLORS = [
  'bg-[#58a6ff]',
  'bg-[#3fb950]',
  'bg-[#d29922]',
  'bg-[#f778ba]',
];

export function CodeViewer({ submissions, chosenSubmission }: CodeViewerProps) {
  const [activeTab, setActiveTab] = useState(0);

  if (submissions.length === 0) {
    return (
      <div className="rounded-lg bg-[var(--bg-card)] p-4">
        <div className="text-[var(--text-secondary)]">
          Waiting for code submissions...
        </div>
      </div>
    );
  }

  const activeSubmission = submissions.find(s => s.playerIndex === activeTab);

  return (
    <div className="rounded-lg bg-[var(--bg-card)] overflow-hidden">
      <div className="flex border-b border-[var(--border)]">
        {[0, 1, 2, 3].map((idx) => {
          const submission = submissions.find(s => s.playerIndex === idx);
          const isChosen = chosenSubmission === idx;
          return (
            <button
              key={idx}
              onClick={() => setActiveTab(idx)}
              className={`
                px-4 py-2 text-sm font-medium transition-colors
                ${activeTab === idx ? TAB_COLORS[idx] + ' text-black' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}
                ${isChosen ? 'ring-2 ring-white ring-inset' : ''}
                ${!submission ? 'opacity-50' : ''}
              `}
            >
              P{idx + 1}
              {isChosen && ' *'}
            </button>
          );
        })}
      </div>
      <div className="p-4">
        {activeSubmission ? (
          <pre className="text-sm overflow-x-auto whitespace-pre-wrap font-mono text-[var(--text-primary)]">
            <code>{activeSubmission.code}</code>
          </pre>
        ) : (
          <div className="text-[var(--text-secondary)]">
            No submission from Player {activeTab + 1}
          </div>
        )}
      </div>
    </div>
  );
}
