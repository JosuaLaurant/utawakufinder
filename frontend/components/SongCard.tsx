'use client'

import { SongEntry } from '@/types'
import { useRouter } from 'next/navigation'
import EmbeddedPlayer from './EmbeddedPlayer'

interface SongCardProps {
  song: SongEntry
}

export default function SongCard({ song }: SongCardProps) {
  const router = useRouter()

  const handleSongClick = (e: React.MouseEvent) => {
    e.stopPropagation() // 부모의 onClick 이벤트 방지
    if (song.song_master_id) {
      router.push(`/song/${song.song_master_id}`)
    }
  }

  const handleArtistClick = (e: React.MouseEvent) => {
    e.stopPropagation() // 부모의 onClick 이벤트 방지
    router.push(`/artist/${encodeURIComponent(song.song_artist)}`)
  }

  const handleUtaiteClick = (e: React.MouseEvent) => {
    e.stopPropagation() // 부모의 onClick 이벤트 방지
    router.push(`/utaite/${encodeURIComponent(song.singer)}`)
  }

  const timeToSeconds = (timeStr: string): number => {
    const parts = timeStr.split(':').map(Number)
    if (parts.length === 3) {
      return parts[0] * 3600 + parts[1] * 60 + parts[2]
    } else if (parts.length === 2) {
      return parts[0] * 60 + parts[1]
    }
    return 0
  }

  const formatDate = (dateStr: string): string => {
    try {
      return new Date(dateStr).toLocaleDateString('ko-KR')
    } catch {
      return dateStr
    }
  }

  return (
    <div className="bg-youtube-gray rounded-lg overflow-hidden hover:bg-youtube-lightgray transition-colors duration-200">
      {/* 임베디드 플레이어 */}
      <div className="relative">
        <EmbeddedPlayer
          videoId={song.video_id}
          startTime={timeToSeconds(song.start_time)}
          title={song.song_name}
        />
        
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-80 text-white text-xs px-2 py-1 rounded">
          {formatDate(song.date)}
        </div>
      </div>

      {/* 컨텐츠 */}
      <div className="p-3">
        <h3 
          className="text-white font-semibold text-base mb-1 line-clamp-2 hover:text-youtube-red transition-colors cursor-pointer"
          onClick={handleSongClick}
          title="이 곡의 다른 기록들 보기"
        >
          {song.song_name}
        </h3>
        <p 
          className="text-gray-300 text-sm mb-1 hover:text-youtube-red transition-colors cursor-pointer"
          onClick={handleArtistClick}
          title="이 아티스트의 다른 곡들 보기"
        >
          {song.song_artist}
        </p>
        <p 
          className="text-gray-400 text-xs hover:text-youtube-red transition-colors cursor-pointer"
          onClick={handleUtaiteClick}
          title="이 우타이테의 다른 노래들 보기"
        >
          우타이테: {song.singer || '미상'}
        </p>
      </div>
    </div>
  )
}