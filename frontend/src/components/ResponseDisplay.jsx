/**
 * ResponseDisplay component shows the AI-generated answer.
 * Formats the response with proper styling and metadata.
 */

function ResponseDisplay({ response }) {
  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Answer</h2>
        <span className="text-sm text-gray-500">
          Response time: {response.response_time_ms}ms
        </span>
      </div>
      
      <div className="prose max-w-none">
        <p className="text-gray-800 leading-relaxed whitespace-pre-line">
          {response.answer}
        </p>
      </div>

      {response.timestamp && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Generated at: {formatDate(response.timestamp)}
          </p>
        </div>
      )}
    </div>
  )
}

export default ResponseDisplay
