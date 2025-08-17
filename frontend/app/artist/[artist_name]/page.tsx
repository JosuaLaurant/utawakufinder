'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Header from '@/components/Header'
import SongCard from '@/components/SongCard'
import { SongEntry } from '@/types'
import { Music, Users, Calendar, PlayCircle, ArrowLeft, ExternalLink } from 'lucide-react'

interface GroupedSong {
  song_id: number
  song_title: string
  performances: SongEntry[]
}

export default function ArtistPage() {
  const params = useParams()
  const router = useRouter()
  const artist_name = decodeURIComponent(params?.artist_name as string)
  
  const [artistSongs, setArtistSongs] = useState<GroupedSong[]>([])
  const [loading, setLoading] = useState(true)
  const [artistStats, setArtistStats] = useState<{
    totalSongs: number
    totalPerformances: number
    uniqueSingers: string[]
    latestPerformance: SongEntry | null
    firstPerformance: SongEntry | null
  } | null>(null)

  useEffect(() => {
    if (artist_name) {
      fetchArtistDetails()
    }
  }, [artist_name])

  const fetchArtistDetails = async () => {
    console.log('🎤 아티스트 상세 정보 가져오기 시작:', artist_name)
    
    try {
      // 아티스트의 모든 곡과 공연 기록 가져오기
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9030'
      const response = await fetch(`${backendUrl}/artists/songs?name=${encodeURIComponent(artist_name)}`)
      
      if (!response.ok) {
        throw new Error('아티스트 정보를 찾을 수 없습니다.')
      }
      
      const data = await response.json()
      
      // API 응답 (PerformanceDetail[])을 곡별로 그룹화
      const songsMap = new Map<number, GroupedSong>()
      
      data.forEach((performance: SongEntry) => {
        if (!songsMap.has(performance.song_id)) {
          songsMap.set(performance.song_id, {
            song_id: performance.song_id,
            song_title: performance.song_title,
            performances: []
          })
        }
        songsMap.get(performance.song_id)!.performances.push(performance)
      })
      
      const groupedSongs = Array.from(songsMap.values())
      setArtistSongs(groupedSongs)
      console.log('✅ 아티스트 곡 정보:', groupedSongs.length, '곡')

      // 통계 계산
      const allPerformances = data
      const uniqueSingers = Array.from(new Set(allPerformances.map((p: SongEntry) => p.utaite_name)))
      
      // 최신/최오래된 공연 찾기
      const sortedPerformances = allPerformances.sort((a: SongEntry, b: SongEntry) => 
        new Date(b.date).getTime() - new Date(a.date).getTime()
      )
      
      setArtistStats({
        totalSongs: groupedSongs.length,
        totalPerformances: allPerformances.length,
        uniqueSingers,
        latestPerformance: sortedPerformances[0] || null,
        firstPerformance: sortedPerformances[sortedPerformances.length - 1] || null
      })
      
      console.log('✅ 아티스트 통계 계산 완료')
      
    } catch (error) {
      console.error('❌ 아티스트 정보 가져오기 실패:', error)
      alert(`아티스트 정보를 가져오는 중 오류가 발생했습니다: ${error.message}`)
    } finally {
      setLoading(false)
    }
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

  if (!artistStats) {
    return (
      <div className="min-h-screen bg-youtube-dark">
        <Header />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-white">아티스트를 찾을 수 없습니다.</div>
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

        {/* 아티스트 정보 헤더 */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="bg-youtube-gray rounded-lg p-8">
            <div className="flex items-start gap-6">
              {/* 썸네일 */}
              {artistStats.latestPerformance && (
                <div className="flex-shrink-0">
                  <img 
                    src={artistStats.latestPerformance.thumbnail_url} 
                    alt={artist_name}
                    className="w-48 h-32 object-cover rounded-lg"
                  />
                </div>
              )}
              
              {/* 아티스트 정보 */}
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-3 flex items-center">
                  <Music className="w-8 h-8 mr-3 text-youtube-red" />
                  {artist_name}
                </h1>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  <div className="flex items-center gap-2 text-gray-400">
                    <Music className="w-5 h-5" />
                    <span>{artistStats.totalSongs}곡 보유</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-400">
                    <PlayCircle className="w-5 h-5" />
                    <span>{artistStats.totalPerformances}회 불림</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-400">
                    <Users className="w-5 h-5" />
                    <span>{artistStats.uniqueSingers.length}명의 우타이테</span>
                  </div>
                  
                  {artistStats.firstPerformance && (
                    <div className="flex items-center gap-2 text-gray-400">
                      <Calendar className="w-5 h-5" />
                      <span>첫 등록: {new Date(artistStats.firstPerformance.date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
                
                {/* 우타이테들 */}
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-2">이 아티스트의 곡을 부른 우타이테들:</p>
                  <div className="flex flex-wrap gap-2">
                    {artistStats.uniqueSingers.map(singer => {
                      const count = artistSongs.flatMap(song => song.performances)
                        .filter(p => p.utaite_name === singer).length
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

        {/* 아티스트의 곡들 */}
        <div className="max-w-6xl mx-auto">
          <h3 className="text-2xl font-bold text-white mb-6">
            {artist_name}의 곡들 ({artistSongs.length}곡)
          </h3>
          
          {artistSongs.map((artistSong) => (
            <div key={artistSong.song_id} className="mb-8">
              {/* 곡 제목과 정보 */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <h4 
                    className="text-xl font-semibold text-white hover:text-youtube-red transition-colors cursor-pointer"
                    onClick={() => router.push(`/song/${artistSong.song_id}`)}
                  >
                    {artistSong.song_title}
                  </h4>
                  <span className="text-gray-400 text-sm">
                    {artistSong.performances.length}회 불림
                  </span>
                </div>
              </div>
              
              {/* 해당 곡의 공연 기록들 - 가로 스크롤 */}
              <div className="flex gap-4 overflow-x-auto pb-4 custom-scrollbar">
                <div className="flex gap-4 min-w-max">
                  {artistSong.performances.map((performance) => (
                    <div key={performance.id} className="flex-shrink-0 w-80">
                      <SongCard song={performance} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
          
          {artistSongs.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>아직 이 아티스트의 곡이 등록되지 않았습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}