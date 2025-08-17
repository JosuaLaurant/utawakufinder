'use client'

import { Video } from '@/types'
import { Play, Clock, User } from 'lucide-react'

interface VideoCardProps {
  video: Video
}

export default function VideoCard({ video }: VideoCardProps) {
  const formatDuration = (songs: any[]) => {
    return `${songs.length}곡`
  }

  const handleVideoClick = () => {
    window.open(`https://www.youtube.com/watch?v=${video.id}`, '_blank')
  }

  return (
    <div className="bg-youtube-gray rounded-lg overflow-hidden hover:bg-youtube-lightgray transition-colors cursor-pointer group">
      <div 
        className="relative aspect-video bg-gray-800 flex items-center justify-center"
        onClick={handleVideoClick}
      >
        {video.thumbnail ? (
          <img 
            src={video.thumbnail} 
            alt={video.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
            <Play className="w-12 h-12 text-gray-400" />
          </div>
        )}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
          <Play className="w-12 h-12 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="text-white font-medium text-sm line-clamp-2 mb-2">
          {video.title}
        </h3>
        
        <div className="space-y-1 text-xs text-gray-400">
          <div className="flex items-center">
            <User className="w-3 h-3 mr-1" />
            <span>{video.channel}</span>
          </div>
          
          {video.singer && (
            <div className="flex items-center">
              <span className="w-3 h-3 mr-1 flex items-center justify-center">🎤</span>
              <span>{video.singer}</span>
            </div>
          )}
          
          <div className="flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            <span>{formatDuration(video.songs)}</span>
          </div>
          
          {video.date && (
            <div className="text-gray-500">
              {new Date(video.date).toLocaleDateString('ko-KR')}
            </div>
          )}
        </div>

        <div className="mt-3 space-y-1">
          <h4 className="text-white text-xs font-medium">수록곡:</h4>
          <div className="max-h-20 overflow-y-auto scrollbar-hide">
            {video.songs.slice(0, 3).map((song, index) => (
              <div key={index} className="text-xs text-gray-400 truncate">
                {song.start_time} - {song.song_name} ({song.song_artist})
              </div>
            ))}
            {video.songs.length > 3 && (
              <div className="text-xs text-gray-500">
                +{video.songs.length - 3}곡 더...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}