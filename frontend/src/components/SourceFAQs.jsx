/**
 * SourceFAQs component displays the retrieved FAQs used to generate the answer.
 * Shows relevance scores and allows expanding to see full FAQ details.
 */

import { useState } from 'react'

function SourceFAQs({ sources }) {
  const [expandedId, setExpandedId] = useState(null)

  const toggleExpand = (faqId) => {
    setExpandedId(expandedId === faqId ? null : faqId)
  }

  if (!sources || sources.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">
        Source FAQs ({sources.length})
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        These FAQs were used to generate the answer above:
      </p>

      <div className="space-y-3">
        {sources.map((source) => (
          <div
            key={source.faq_id}
            className="border border-gray-200 rounded-lg overflow-hidden"
          >
            {/* FAQ Header */}
            <div
              onClick={() => toggleExpand(source.faq_id)}
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded">
                    {source.category}
                  </span>
                  <span className="text-sm text-gray-600">
                    Relevance: {(source.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
                <h3 className="text-base font-semibold text-gray-900 mt-2">
                  {source.question}
                </h3>
              </div>
              <svg
                className={`w-5 h-5 text-gray-500 transition-transform ${
                  expandedId === source.faq_id ? 'transform rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>

            {/* Relevance Bar */}
            <div className="px-4 pb-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all"
                  style={{ width: `${source.similarity_score * 100}%` }}
                />
              </div>
            </div>

            {/* FAQ Answer (Expandable) */}
            {expandedId === source.faq_id && (
              <div className="px-4 pb-4 border-t border-gray-200 pt-4">
                <p className="text-sm font-semibold text-gray-700 mb-2">
                  Full Answer:
                </p>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {source.answer}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default SourceFAQs
