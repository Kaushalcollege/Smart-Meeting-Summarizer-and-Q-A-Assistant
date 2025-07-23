// src/App.jsx

import React, { useState } from "react";
import "./App.css";

function App() {
  // State for inputs
  const [transcript, setTranscript] = useState("");
  const [question, setQuestion] = useState("");

  // State for outputs
  const [summary, setSummary] = useState("");
  const [actionItems, setActionItems] = useState([]);
  const [answer, setAnswer] = useState("");

  // State for UX
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleApiCall = (endpoint, body, onSuccess) => {
    setLoading(true);
    setError("");
    fetch(`http://127.0.0.1:8000${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => onSuccess(data))
      .catch((err) => setError(`Failed to fetch: ${err.message}`))
      .finally(() => setLoading(false));
  };

  const handleSummarize = () => {
    handleApiCall("/summarize", { text: transcript }, (data) =>
      setSummary(data.summary)
    );
  };

  const handleGetActions = () => {
    handleApiCall("/actions", { text: transcript }, (data) =>
      setActionItems(data.action_items)
    );
  };

  const handleAskQuestion = () => {
    handleApiCall("/ask", { question: question, context: transcript }, (data) =>
      setAnswer(data.answer)
    );
  };

  return (
    <div className="App">
      <h1>Smart Meeting Assistant</h1>

      <div className="input-section">
        <h2>Meeting Transcript</h2>
        <textarea
          rows="15"
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Paste your meeting transcript here..."
        />
        <div className="button-group">
          <button onClick={handleSummarize} disabled={loading || !transcript}>
            Generate Summary
          </button>
          <button onClick={handleGetActions} disabled={loading || !transcript}>
            Get Action Items
          </button>
        </div>
      </div>

      {loading && <div className="loading">Processing...</div>}
      {error && <div className="error">{error}</div>}

      <div className="results-section">
        {summary && (
          <div className="result-box">
            <h2>Summary</h2>
            <p>{summary}</p>
          </div>
        )}

        {actionItems.length > 0 && (
          <div className="result-box">
            <h2>Action Items</h2>
            <ul>
              {actionItems.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="result-box qa-section">
          <h2>Ask a Question</h2>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask something about the transcript..."
          />
          <button
            onClick={handleAskQuestion}
            disabled={loading || !question || !transcript}
          >
            Ask
          </button>
          {answer && (
            <p>
              <b>Answer:</b> {answer}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
