'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { Music, Users, PlayCircle, Calendar } from 'lucide-react'

interface Artist {
  name: string
  song_count: number
  total_performances: number
  latest_performance: {
    date: string
    thumbnail: string
    song_title: string
  } | null
  first_performance: {
    date: string
    thumbnail: string
    song_title: string
  } | null
  top_songs: Array<{
    id: string
    title: string
    performance_count: number
  }>
}

export default function ArtistsPage() {
  const router = useRouter()
  const [artists, setArtists] = useState<Artist[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchArtists()
  }, [])

  const fetchArtists = async () => {
    console.log('🎤 전체 아티스트 목록 가져오기 시작')
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9030'
      const response = await fetch(`${backendUrl}/artists`)
      const data = await response.json()
      setArtists(data)
      console.log('✅ 아티스트 목록 조회 성공:', data.length, '명')
    } catch (error) {
      console.error('❌ 아티스트 목록 조회 실패:', error)
      alert(`아티스트 목록을 가져오는 중 오류가 발생했습니다: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleArtistClick = (artistName: string) => {
    router.push(`/artist/${encodeURIComponent(artistName)}`)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-youtube-dark">
        <Header />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-white">로딩 중...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-youtube-dark">
      <Header />
      <div className="pt-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-8 flex items-center">
            <Music className="w-8 h-8 mr-3 text-youtube-red" />
            전체 아티스트 ({artists.length}명)
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {artists.map((artist) => (
              <div
                key={artist.name}
                onClick={() => handleArtistClick(artist.name)}
                className="bg-youtube-gray hover:bg-youtube-lightgray rounded-lg p-6 cursor-pointer transition-colors duration-200"
              >
                {/* 아티스트 썸네일 */}
                <div className="relative mb-4">
                  {artist.latest_performance && (
                    <img
                      src={artist.latest_performance.thumbnail_url || artist.latest_performance.thumbnail}
                      alt={artist.name}
                      className="w-full h-40 object-cover rounded-lg"
                    />
                  )}
                  <div className="absolute bottom-2 right-2 bg-black bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                    {artist.latest_performance && new Date(artist.latest_performance.date).toLocaleDateString()}
                  </div>
                </div>

                {/* 아티스트 정보 */}
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-white mb-2 line-clamp-2">
                    {artist.name}
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                      <Music className="w-4 h-4" />
                      <span>{artist.song_count}곡</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <PlayCircle className="w-4 h-4" />
                      <span>{artist.total_performances}회</span>
                    </div>
                  </div>
                </div>

                {/* 인기 곡들 */}
                <div>
                  <p className="text-sm text-gray-400 mb-2">인기 곡:</p>
                  <div className="space-y-1">
                    {(artist.top_songs || []).slice(0, 3).map((song) => (
                      <div key={song.id} className="flex justify-between items-center text-sm">
                        <span className="text-gray-300 truncate flex-1 mr-2">
                          {song.title}
                        </span>
                        <span className="text-gray-500 text-xs">
                          {song.performance_count}회
                        </span>
                      </div>
                    ))}
                    {(!artist.top_songs || artist.top_songs.length === 0) && (
                      <p className="text-gray-500 text-xs">인기 곡 정보가 없습니다.</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {artists.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>아직 등록된 아티스트가 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}