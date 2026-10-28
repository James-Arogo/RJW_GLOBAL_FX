import React, { useState } from 'react'
import { AlertCircle, X } from 'lucide-react'

export const DisclaimerBanner = () => {
  const [visible, setVisible] = useState(true)

  if (!visible) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-warning-500/10 border-b border-warning-500/30 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-start gap-3 justify-between">
        <div className="flex items-start gap-3 flex-1">
          <AlertCircle className="w-5 h-5 text-warning-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-warning-300">⚠️ SIMULATED GAME ONLY</p>
            <p className="text-xs text-warning-200 mt-1">
              This is a simulated forex trading game for learning & fun only. Prices are controlled by the platform. 
              Not connected to real forex markets. Play at your own risk – no real profits/losses outside the app.
            </p>
          </div>
        </div>
        <button
          onClick={() => setVisible(false)}
          className="text-warning-300 hover:text-warning-400 transition-colors flex-shrink-0 p-1"
          aria-label="Close disclaimer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
