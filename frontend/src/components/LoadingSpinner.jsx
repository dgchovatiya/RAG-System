/**
 * LoadingSpinner component displays during API requests.
 * Provides visual feedback that the system is processing.
 */

function LoadingSpinner() {
  return (
    <div className="bg-white rounded-lg shadow-md p-12">
      <div className="flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600"></div>
        <p className="mt-4 text-gray-600 font-medium">
          Searching knowledge base and generating answer...
        </p>
        <p className="mt-2 text-sm text-gray-500">
          This typically takes 2-3 seconds
        </p>
      </div>
    </div>
  )
}

export default LoadingSpinner
