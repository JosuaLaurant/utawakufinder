'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Header from '@/components/Header'
import SongCard from '@/components/SongCard'
import { SongEntry } from '@/types'
import { Music, Users, Calendar, PlayCircle, ArrowLeft, ExternalLink } from 'lucide-react'

interface SongMaster {
  id: number
  titles: { original: string }
  artist: { original: string }
  tags: string[]
  performance_count: number
}

export default function SongPage() {
  const params = useParams()
  const router = useRouter()
  const song_master_id = params?.song_master_id as string
  
  const [songMaster, setSongMaster] = useState<SongMaster | null>(null)
  const [performances, setPerformances] = useState<SongEntry[]>([])
  const [relatedSongs, setRelatedSongs] = useState<SongMaster[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (song_master_id) {
      fetchSongDetails()
    }
  }, [song_master_id])

  const fetchSongDetails = async () => {
    console.log('🎵 곡 상세 정보 가져오기 시작:', song_master_id)
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9030'
      
      // 곡 마스터 정보 가져오기
      const masterResponse = await fetch(`${backendUrl}/songs/master`)
      const masterData = await masterResponse.json()
      const master = masterData.find((m: SongMaster) => m.id === parseInt(song_master_id))
      
      if (!master) {
        throw new Error('곡을 찾을 수 없습니다.')
      }
      
      setSongMaster(master)
      console.log('✅ 곡 마스터 정보:', master.titles.original)

      // 해당 곡을 부른 모든 기록 가져오기
      const performancesResponse = await fetch(`${backendUrl}/songs/by-master/${song_master_id}`)
      
      if (!performancesResponse.ok) {
        throw new Error('부른 기록을 가져올 수 없습니다.')
      }
      
      const performancesData = await performancesResponse.json()
      
      // API가 배열을 반환하는지 확인
      const performances = Array.isArray(performancesData) ? performancesData : []
      
      setPerformances(performances)
      console.log('✅ 부른 기록:', performances.length, '개')

      // 같은 아티스트의 다른 곡들 찾기
      const relatedArtistSongs = masterData.filter((m: SongMaster) => 
        m.id !== song_master_id && 
        m.artist.original === master.artist.original
      ).slice(0, 6) // 최대 6개까지
      
      setRelatedSongs(relatedArtistSongs)
      console.log('✅ 관련 곡:', relatedArtistSongs.length, '개')
      
    } catch (error) {
      console.error('❌ 곡 정보 가져오기 실패:', error)
      alert(`곡 정보를 가져오는 중 오류가 발생했습니다: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const uniqueSingers = Array.from(new Set(performances.map(p => p.utaite_name)))
  const latestPerformance = performances.length > 0 ? performances[performances.length - 1] : null
  const firstPerformance = performances.length > 0 ? performances[0] : null

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

  if (!songMaster) {
    return (
      <div className="min-h-screen bg-youtube-dark">
        <Header />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-white">곡을 찾을 수 없습니다.</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-youtube-dark">
      <Header />
      <div className="pt-20 px-6">
        {/* 뒤로가기 버튼 */}
        <div className="max-w-6xl mx-auto mb-4">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>뒤로가기</span>
          </button>
        </div>

        {/* 곡 정보 헤더 */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="bg-youtube-gray rounded-lg p-8">
            <div className="flex items-start gap-6">
              {/* 썸네일 */}
              {latestPerformance && (
                <div className="flex-shrink-0">
                  <img 
                    src={latestPerformance.thumbnail_url} 
                    alt={songMaster.titles.original}
                    className="w-48 h-32 object-cover rounded-lg"
                  />
                </div>
              )}
              
              {/* 곡 정보 */}
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-3 flex items-center">
                  <Music className="w-8 h-8 mr-3 text-youtube-red" />
                  {songMaster.titles.original}
                </h1>
                
                <h2 className="text-xl text-gray-300 mb-4">
                  {songMaster.artist.original}
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="flex items-center gap-2 text-gray-400">
                    <PlayCircle className="w-5 h-5" />
                    <span>{songMaster.performance_count}회 부름</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-400">
                    <Users className="w-5 h-5" />
                    <span>{uniqueSingers.length}명의 우타이테</span>
                  </div>
                  
                  {firstPerformance && (
                    <div className="flex items-center gap-2 text-gray-400">
                      <Calendar className="w-5 h-5" />
                      <span>첫 등록: {new Date(firstPerformance.date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
                
                {/* 우타이테들 */}
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-2">이 곡을 부른 우타이테들:</p>
                  <div className="flex flex-wrap gap-2">
                    {uniqueSingers.map(singer => {
                      const count = performances.filter(p => p.utaite_name === singer).length
                      return (
                        <span 
                          key={singer}
                          className="px-3 py-1 bg-youtube-red text-white rounded-full text-sm"
                        >
                          {singer} ({count}회)
                        </span>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 부른 기록 목록 */}
        <div className="max-w-6xl mx-auto mb-12">
          <h3 className="text-2xl font-bold text-white mb-6">
            이 곡을 부른 기록 ({performances.length}개)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {performances.map((performance) => (
              <SongCard key={performance.id} song={performance} />
            ))}
          </div>
          
          {performances.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>아직 이 곡을 부른 기록이 없습니다.</p>
            </div>
          )}
        </div>

        {/* 관련 곡들 */}
        {relatedSongs.length > 0 && (
          <div className="max-w-6xl mx-auto">
            <h3 className="text-2xl font-bold text-white mb-6">
              {songMaster?.artist.original}의 다른 곡들
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {relatedSongs.map((related) => (
                <div
                  key={related.id}
                  onClick={() => router.push(`/song/${related.id}`)}
                  className="bg-youtube-gray hover:bg-youtube-lightgray rounded-lg p-4 cursor-pointer transition-colors"
                >
                  <h4 className="text-white font-semibold text-sm mb-2 line-clamp-2">
                    {related.titles.original}
                  </h4>
                  <p className="text-gray-400 text-xs">
                    {related.performance_count}회 부름
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}