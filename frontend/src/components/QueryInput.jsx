/**
 * QueryInput component for user question submission.
 * Handles text input and form submission.
 */

function QueryInput({ query, setQuery, onSubmit, loading }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <form onSubmit={onSubmit}>
        <label htmlFor="query" className="block text-lg font-semibold text-gray-900 mb-3">
          Ask your legal question:
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., What is the statute of limitations for personal injury claims?"
          rows="4"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
          disabled={loading}
          maxLength={500}
        />
        <div className="flex justify-between items-center mt-4">
          <span className="text-sm text-gray-500">
            {query.length}/500 characters
          </span>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-all ${
              loading || !query.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg'
            }`}
          >
            {loading ? 'Searching...' : 'Ask Question'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default QueryInput
