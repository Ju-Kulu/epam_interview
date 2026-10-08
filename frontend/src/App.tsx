import { useRef, useState, type FormEvent } from 'react';

type ChatRequest = {
    question: string;
};

type SourceReference = {
    chunk_id: string;
    document: string;
    title: string | null;
    distance: number;
};

type ChatResponse = {
    answer: string;
    sources: SourceReference[];
};

type ChatTurn = {
    id: number;
    question: string;
    response?: ChatResponse;
};

function isSourceReference(value: unknown): value is SourceReference {
    if (typeof value !== 'object' || value === null) return false;
    const source = value as Record<string, unknown>;
    return (
        typeof source.chunk_id === 'string' &&
        typeof source.document === 'string' &&
        (typeof source.title === 'string' || source.title === null) &&
        typeof source.distance === 'number'
    );
}

function isChatResponse(value: unknown): value is ChatResponse {
    if (typeof value !== 'object' || value === null) return false;
    const response = value as Record<string, unknown>;
    return (
        typeof response.answer === 'string' &&
        Array.isArray(response.sources) &&
        response.sources.every(isSourceReference)
    );
}

function getErrorMessage(payload: unknown, status: number): string {
    if (typeof payload === 'object' && payload !== null) {
        const detail = (payload as Record<string, unknown>).detail;
        if (typeof detail === 'string') return detail;
    }
    return `The request failed (HTTP ${status}). Please try again.`;
}

export default function App() {
    const [question, setQuestion] = useState('');
    const [turns, setTurns] = useState<ChatTurn[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const nextTurnId = useRef(0);

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const submittedQuestion = question.trim();
        if (!submittedQuestion || isLoading) return;

        const turnId = nextTurnId.current++;
        setTurns((current) => [...current, { id: turnId, question: submittedQuestion }]);
        setQuestion('');
        setError(null);
        setIsLoading(true);

        try {
            const request: ChatRequest = { question: submittedQuestion };
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request),
            });
            const payload: unknown = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(getErrorMessage(payload, response.status));
            }
            if (!isChatResponse(payload)) {
                throw new Error('The service returned an unexpected response. Please try again.');
            }

            setTurns((current) =>
                current.map((turn) => (turn.id === turnId ? { ...turn, response: payload } : turn)),
            );
        } catch (requestError) {
            setError(
                requestError instanceof Error
                    ? requestError.message
                    : 'Unable to reach the knowledge base. Please try again.',
            );
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="app-shell">
            <header className="topbar">
                <div className="brand-mark" aria-hidden="true">O</div>
                <div className="brand-copy">
                    <span>OmniCorp Solutions</span>
                    <strong>Knowledge desk</strong>
                </div>
                <div className="service-state"><span /> Internal knowledge base</div>
            </header>

            <main className="workspace">
                <section className="intro" aria-labelledby="page-title">
                    <p className="eyebrow">CUSTOMER SUCCESS</p>
                    <h1 id="page-title">What can we<br />help you solve?</h1>
                    <p className="intro-copy">
                        Ask about authentication, payments, integrations, or configuration issues.
                    </p>
                </section>

                <section className="chat-panel" aria-label="Knowledge base chat">
                    <div className="conversation" aria-live="polite">
                        {turns.length === 0 ? (
                            <div className="empty-state">
                                <span className="empty-icon" aria-hidden="true">?</span>
                                <p>Your conversation will appear here.</p>
                            </div>
                        ) : (
                            turns.map((turn, index) => (
                                <div className="turn" key={turn.id}>
                                    <div className="question-row">
                                        <span className="speaker-label">YOU</span>
                                        <p className="question-bubble">{turn.question}</p>
                                    </div>
                                    {turn.response ? (
                                        <article className="answer-block">
                                            <div className="answer-heading">
                                                <span className="assistant-mark" aria-hidden="true">O</span>
                                                <span>Knowledge desk</span>
                                            </div>
                                            <p className="answer-text">{turn.response.answer}</p>
                                            {turn.response.sources.length > 0 ? (
                                                <div className="source-list">
                                                    <h2>Sources</h2>
                                                    {turn.response.sources.map((source) => (
                                                        <div className="source-row" key={source.chunk_id}>
                                                            <span className="source-document">{source.title ?? source.document}</span>
                                                            <span className="source-detail">
                                                                {source.document} · {source.chunk_id} · distance {source.distance.toFixed(2)}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <p className="no-sources">No source references returned.</p>
                                            )}
                                        </article>
                                    ) : isLoading && index === turns.length - 1 ? (
                                        <div className="answer-block loading-answer" role="status">
                                            <span className="assistant-mark" aria-hidden="true">O</span>
                                            <span>Searching the knowledge base</span>
                                            <span className="loading-dots" aria-hidden="true">...</span>
                                        </div>
                                    ) : null}
                                </div>
                            ))
                        )}
                    </div>

                    {error && <p className="error-message" role="alert">{error}</p>}

                    <form className="composer" onSubmit={handleSubmit}>
                        <label htmlFor="question">Ask a question</label>
                        <div className="composer-row">
                            <textarea
                                id="question"
                                name="question"
                                placeholder="e.g. What should OAuth redirect URLs use?"
                                rows={2}
                                value={question}
                                onChange={(event) => setQuestion(event.target.value)}
                                disabled={isLoading}
                            />
                            <button type="submit" disabled={isLoading || !question.trim()}>
                                {isLoading ? 'Sending…' : 'Send'}
                                <span aria-hidden="true">→</span>
                            </button>
                        </div>
                    </form>
                </section>
            </main>

            <footer className="footer-note">Answers are grounded in the internal knowledge base.</footer>
        </div>
    );
}
