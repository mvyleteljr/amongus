import type { TestResult } from '../types/game';

interface TestResultsProps {
  results: TestResult | null;
}

export function TestResults({ results }: TestResultsProps) {
  if (!results) {
    return null;
  }

  return (
    <div className="rounded-lg bg-[var(--bg-card)] p-4">
      <h3 className="text-lg font-bold mb-4">Test Results</h3>
      
      <div className={`text-2xl font-bold mb-2 ${results.passed ? 'text-[var(--success)]' : 'text-[var(--failure)]'}`}>
        {results.passed ? 'PASSED' : 'FAILED'}
      </div>
      
      <div className="text-sm text-[var(--text-secondary)] mb-4">
        {results.passedTests}/{results.totalTests} tests passed
      </div>

      {results.failedTests.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-[var(--failure)]">Failed Tests:</h4>
          {results.failedTests.slice(0, 3).map((fail, idx) => (
            <div key={idx} className="text-xs bg-[var(--bg-secondary)] p-2 rounded">
              <div>Test {fail.testIndex + 1}</div>
              <div className="text-[var(--text-secondary)]">
                Input: {JSON.stringify(fail.input)}
              </div>
              <div className="text-[var(--text-secondary)]">
                Expected: {JSON.stringify(fail.expected)}
              </div>
              {fail.actual !== undefined && (
                <div className="text-[var(--failure)]">
                  Got: {JSON.stringify(fail.actual)}
                </div>
              )}
              {fail.error && (
                <div className="text-[var(--failure)]">
                  Error: {fail.error}
                </div>
              )}
            </div>
          ))}
          {results.failedTests.length > 3 && (
            <div className="text-xs text-[var(--text-secondary)]">
              ...and {results.failedTests.length - 3} more
            </div>
          )}
        </div>
      )}
    </div>
  );
}
