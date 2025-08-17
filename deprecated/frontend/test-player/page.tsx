'use client'

import { useEffect, useState } from 'react'

export default function TestPlayerPage() {
  const [apiStatus, setApiStatus] = useState('Loading...')
  const [playerStatus, setPlayerStatus] = useState('Not created')

  useEffect(() => {
    // YouTube API 상태 체크
    const checkAPI = () => {
      if (typeof window !== 'undefined') {
        if (window.YT && window.YT.Player) {
          setApiStatus('✅ YouTube API Loaded')
          createTestPlayer()
        } else {
          setApiStatus('❌ YouTube API Not Loaded')
          window.onYouTubeIframeAPIReady = () => {
            setApiStatus('✅ YouTube API Ready via Callback')
            createTestPlayer()
          }
        }
      }
    }

    const createTestPlayer = () => {
      try {
        const player = new window.YT.Player('test-player', {
          height: '200',
          width: '300',
          videoId: 'dQw4w9WgXcQ', // Rick Roll for testing
          events: {
            onReady: () => {
              setPlayerStatus('✅ Player Ready')
            },
            onError: (event: any) => {
              setPlayerStatus(`❌ Player Error: ${event.data}`)
            }
          }
        })
      } catch (error) {
        setPlayerStatus(`❌ Player Creation Failed: ${error}`)
      }
    }

    checkAPI()
  }, [])

  return (
    <div className="min-h-screen bg-youtube-dark p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">YouTube Player API Test</h1>
        
        <div className="space-y-4 mb-8">
          <div className="bg-youtube-gray p-4 rounded">
            <h2 className="text-white font-semibold mb-2">API Status:</h2>
            <p className="text-gray-300">{apiStatus}</p>
          </div>
          
          <div className="bg-youtube-gray p-4 rounded">
            <h2 className="text-white font-semibold mb-2">Player Status:</h2>
            <p className="text-gray-300">{playerStatus}</p>
          </div>
          
          <div className="bg-youtube-gray p-4 rounded">
            <h2 className="text-white font-semibold mb-2">Environment Info:</h2>
            <p className="text-gray-300">User Agent: {typeof window !== 'undefined' ? navigator.userAgent : 'Server'}</p>
            <p className="text-gray-300">Current URL: {typeof window !== 'undefined' ? window.location.href : 'Server'}</p>
          </div>
        </div>

        <div className="bg-youtube-gray p-4 rounded">
          <h2 className="text-white font-semibold mb-4">Test Player:</h2>
          <div id="test-player"></div>
        </div>

        <div className="mt-8 bg-youtube-gray p-4 rounded">
          <h2 className="text-white font-semibold mb-2">Manual Tests:</h2>
          <div className="space-y-2">
            <button 
              onClick={() => {
                const script = document.createElement('script')
                script.src = 'https://www.youtube.com/iframe_api'
                document.head.appendChild(script)
                setApiStatus('🔄 Manually loading API...')
              }}
              className="bg-blue-600 text-white px-4 py-2 rounded mr-2"
            >
              Manually Load API
            </button>
            
            <button 
              onClick={() => {
                console.log('Window.YT:', window.YT)
                console.log('YT.Player:', window.YT?.Player)
                setApiStatus(`Window.YT exists: ${!!window.YT}, YT.Player exists: ${!!window.YT?.Player}`)
              }}
              className="bg-green-600 text-white px-4 py-2 rounded"
            >
              Check Console
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}