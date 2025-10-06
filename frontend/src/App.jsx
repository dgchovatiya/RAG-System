import { useState, useEffect } from 'react'
import QueryInput from './components/QueryInput'
import ResponseDisplay from './components/ResponseDisplay'
import SourceFAQs from './components/SourceFAQs'
import InteractionLog from './components/InteractionLog'
import LoadingSpinner from './components/LoadingSpinner'
import { askQuestion, getInteractionLogs } from './services/api'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [logs, setLogs] = useState([])
  const [showLogs, setShowLogs] = useState(false)

  // Sample questions to help users get started
  const sampleQuestions = [
    "What is the statute of limitations for personal injury?",
    "Can I break a contract without penalty?",
    "What constitutes wrongful termination?",
    "What are my rights if I'm arrested?"
  ]

  useEffect(() => {
    loadLogs()
  }, [])

  const loadLogs = async () => {
    try {
      const data = await getInteractionLogs(20)
      setLogs(data)
    } catch (err) {
      console.error('Failed to load logs:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!query.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const data = await askQuestion(query)
      setResponse(data)
      await loadLogs() // Refresh logs after new query
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSampleClick = (sampleQuery) => {
    setQuery(sampleQuery)
  }

  const handleLogClick = (log) => {
    setQuery(log.user_query)
    // Reconstruct response from log
    const logResponse = {
      answer: log.ai_response,
      sources: [],
      response_time_ms: log.response_time_ms,
      timestamp: log.timestamp
    }
    setResponse(logResponse)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Legal Q&A System</h1>
              <p className="text-sm text-gray-600 mt-1">AI-powered legal information assistant</p>
            </div>
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              {showLogs ? 'Hide History' : 'Show History'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Query Section */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Sample Questions */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                Try these sample questions:
              </h2>
              <div className="flex flex-wrap gap-2">
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSampleClick(q)}
                    className="px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg text-sm hover:bg-indigo-200 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Query Input */}
            <QueryInput
              query={query}
              setQuery={setQuery}
              onSubmit={handleSubmit}
              loading={loading}
            />

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {/* Loading Spinner */}
            {loading && <LoadingSpinner />}

            {/* Response Display */}
            {response && !loading && (
              <>
                <ResponseDisplay response={response} />
                {response.sources && response.sources.length > 0 && (
                  <SourceFAQs sources={response.sources} />
                )}
              </>
            )}
          </div>

          {/* Sidebar - Interaction Log */}
          <div className="lg:col-span-1">
            {showLogs && (
              <InteractionLog
                logs={logs}
                onLogClick={handleLogClick}
              />
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-600">
            <span className="font-semibold">Disclaimer:</span> This system provides general legal information only, 
            not legal advice. Consult with a qualified attorney for your specific situation.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
