/**
 * InteractionLog component displays history of user queries.
 * Allows clicking on previous queries to view them again.
 */

function InteractionLog({ logs, onLogClick }) {
  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const truncateText = (text, maxLength = 60) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        Recent Queries
      </h2>

      {logs.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">
          No queries yet. Ask your first question!
        </p>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {logs.map((log, idx) => (
            <div
              key={log.id || idx}
              onClick={() => onLogClick(log)}
              className="p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-indigo-50 hover:border-indigo-300 transition-all"
            >
              <p className="text-sm font-medium text-gray-900 mb-1">
                {truncateText(log.user_query)}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{formatDate(log.timestamp)}</span>
                <span>{log.response_time_ms}ms</span>
              </div>
              {log.error_occurred && (
                <span className="inline-block mt-1 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">
                  Error
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Total queries: {logs.length}
        </p>
      </div>
    </div>
  )
}

export default InteractionLog
