'use client'

import { useState } from 'react'
import { usePlayer } from '@/contexts/PlayerContext'
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, X } from 'lucide-react'

export default function GlobalPlayer() {
  const { playerState, isPlayerReady, play, pause, stop, setVolume, seekTo } = usePlayer()
  const [showVolumeSlider, setShowVolumeSlider] = useState(false)
  const [showDebug, setShowDebug] = useState(false)

  if (!playerState.currentSong) {
    // 플레이어 준비 상태만 표시 (곡이 없을 때)
    if (!isPlayerReady) {
      return (
        <div className="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg z-50">
          🎵 음악 플레이어 로딩 중... (Ready: {isPlayerReady ? 'YES' : 'NO'})
        </div>
      )
    }
    return (
      <div className="fixed bottom-4 right-4 bg-green-800 text-white px-4 py-2 rounded-lg z-50 cursor-pointer"
           onClick={() => {
             console.log('Player ready:', isPlayerReady)
             console.log('Window.YT:', window.YT)
             console.log('YT.Player:', window.YT?.Player)
           }}>
        ✅ 음악 플레이어 준비 완료 (클릭하여 상태 확인)
      </div>
    )
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    const newTime = percent * playerState.duration
    seekTo(newTime)
  }

  const progress = playerState.duration > 0 ? (playerState.currentTime / playerState.duration) * 100 : 0

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 p-4 z-50">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between">
          {/* 왼쪽: 현재 재생 중인 곡 정보 */}
          <div className="flex items-center space-x-4 flex-1 min-w-0">
            <img
              src={`https://img.youtube.com/vi/${playerState.currentSong.videoId}/mqdefault.jpg`}
              alt={playerState.currentSong.title}
              className="w-16 h-12 object-cover rounded"
            />
            <div className="min-w-0 flex-1">
              <h4 className="text-white font-semibold text-sm truncate">
                {playerState.currentSong.title}
              </h4>
              <p className="text-gray-400 text-xs truncate">
                {playerState.currentSong.artist} • {playerState.currentSong.utaite}
              </p>
            </div>
          </div>

          {/* 가운데: 재생 컨트롤 */}
          <div className="flex flex-col items-center space-y-2 flex-1 max-w-md">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => seekTo(Math.max(0, playerState.currentTime - 10))}
                className="text-gray-400 hover:text-white transition-colors"
                title="10초 뒤로"
              >
                <SkipBack className="w-5 h-5" />
              </button>
              
              <button
                onClick={playerState.isPlaying ? pause : () => play(playerState.currentSong!)}
                className="bg-white hover:bg-gray-200 text-black p-2 rounded-full transition-colors"
                title={playerState.isPlaying ? "일시정지" : "재생"}
              >
                {playerState.isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
              </button>
              
              <button
                onClick={() => seekTo(Math.min(playerState.duration, playerState.currentTime + 10))}
                className="text-gray-400 hover:text-white transition-colors"
                title="10초 앞으로"
              >
                <SkipForward className="w-5 h-5" />
              </button>
            </div>

            {/* 진행 바 */}
            <div className="w-full flex items-center space-x-2">
              <span className="text-xs text-gray-400 w-10 text-right">
                {formatTime(playerState.currentTime)}
              </span>
              <div
                className="flex-1 h-1 bg-gray-600 rounded-full cursor-pointer"
                onClick={handleProgressClick}
              >
                <div
                  className="h-full bg-white rounded-full transition-all duration-100"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="text-xs text-gray-400 w-10">
                {formatTime(playerState.duration)}
              </span>
            </div>
          </div>

          {/* 오른쪽: 볼륨 컨트롤 및 닫기 */}
          <div className="flex items-center space-x-4 flex-1 justify-end">
            <div className="relative">
              <button
                onClick={() => setShowVolumeSlider(!showVolumeSlider)}
                className="text-gray-400 hover:text-white transition-colors"
                title="볼륨"
              >
                {playerState.volume === 0 ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
              </button>
              
              {showVolumeSlider && (
                <div className="absolute bottom-full right-0 mb-2 bg-gray-800 p-3 rounded-lg">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={playerState.volume}
                    onChange={(e) => setVolume(Number(e.target.value))}
                    className="w-20 accent-white"
                    title={`볼륨: ${playerState.volume}%`}
                  />
                </div>
              )}
            </div>
            
            <button
              onClick={stop}
              className="text-gray-400 hover:text-white transition-colors"
              title="플레이어 닫기"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}