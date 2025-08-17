'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { Music, Users, PlayCircle, Calendar, Mic } from 'lucide-react'

interface Utaite {
  id: number
  name: string
  name_korean?: string
  name_english?: string
  name_romanized?: string
  total_performances: number
  unique_songs: number
  unique_artists: number
  latest_performance?: {
    date: string
    thumbnail_url: string
    song_title: string
  }
  first_performance?: {
    date: string
    thumbnail_url: string
    song_title: string
  }
  top_songs: Array<{
    id: number
    title: string
    artist_name: string
    performance_count: number
  }>
}

export default function UtaitesPage() {
  const router = useRouter()
  const [utaites, setUtaites] = useState<Utaite[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUtaites()
  }, [])

  const fetchUtaites = async () => {
    console.log('🎤 전체 우타이테 목록 가져오기 시작')
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/utaites`)
      const data = await response.json()
      setUtaites(data)
      console.log('✅ 우타이테 목록 조회 성공:', data.length, '명')
    } catch (error) {
      console.error('❌ 우타이테 목록 조회 실패:', error)
      alert(`우타이테 목록을 가져오는 중 오류가 발생했습니다: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleUtaiteClick = (utaiteName: string) => {
    router.push(`/utaite/${encodeURIComponent(utaiteName)}`)
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
            <Mic className="w-8 h-8 mr-3 text-youtube-red" />
            전체 우타이테 ({utaites.length}명)
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {utaites.map((utaite) => (
              <div
                key={utaite.name}
                onClick={() => handleUtaiteClick(utaite.name)}
                className="bg-youtube-gray hover:bg-youtube-lightgray rounded-lg p-6 cursor-pointer transition-colors duration-200"
              >
                {/* 우타이테 썸네일 */}
                <div className="relative mb-4">
                  {utaite.latest_performance && (
                    <img
                      src={utaite.latest_performance.thumbnail_url}
                      alt={utaite.name}
                      className="w-full h-40 object-cover rounded-lg"
                    />
                  )}
                  <div className="absolute bottom-2 right-2 bg-black bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                    {utaite.latest_performance && new Date(utaite.latest_performance.date).toLocaleDateString()}
                  </div>
                </div>

                {/* 우타이테 정보 */}
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-white mb-2 line-clamp-2">
                    {utaite.name}
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-400 mb-3">
                    <div className="flex items-center gap-2">
                      <PlayCircle className="w-4 h-4" />
                      <span>{utaite.total_performances}회</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Music className="w-4 h-4" />
                      <span>{utaite.unique_songs}곡</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      <span>{utaite.unique_artist_count}아티스트</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(utaite.first_date).toLocaleDateString()}부터</span>
                    </div>
                  </div>
                </div>

                {/* 우타이테 랭킹 표시 */}
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">활동량</span>
                    <div className="w-20 bg-gray-600 rounded-full h-2">
                      <div 
                        className="bg-youtube-red h-2 rounded-full" 
                        style={{
                          width: `${Math.min((utaite.total_performances / Math.max(...utaites.map(u => u.song_count))) * 100, 100)}%`
                        }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-400">
                    최근: {new Date(utaite.latest_date).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {utaites.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>아직 등록된 우타이테가 없습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}