'use client'

import { Play } from 'lucide-react'

interface EmbeddedPlayerProps {
  videoId: string
  startTime: number
  title: string
  className?: string
}

export default function EmbeddedPlayer({ videoId, startTime, title, className = '' }: EmbeddedPlayerProps) {

  const handlePlay = () => {
    const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}&t=${startTime}s`
    window.open(youtubeUrl, '_blank')
  }

  return (
    <div className={`relative ${className}`}>
      {/* 썸네일과 재생 버튼 */}
      <div className="relative group cursor-pointer">
        <img
          src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
          alt={title}
          className="w-full h-40 object-cover rounded"
        />
        
        {/* 재생 버튼 오버레이 */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center rounded">
          <button
            onClick={handlePlay}
            className="bg-youtube-red hover:bg-red-700 text-white p-3 rounded-full transition-colors opacity-0 group-hover:opacity-100"
            title="YouTube에서 재생"
          >
            <Play className="w-6 h-6" />
          </button>
        </div>

        {/* 재생 시간 표시 */}
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-80 text-white text-xs px-2 py-1 rounded">
          {formatTime(startTime)}
        </div>
      </div>
    </div>
  )
}

function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}