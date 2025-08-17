'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Header from '@/components/Header'
import SongCard from '@/components/SongCard'
import { SongEntry } from '@/types'
import { Music, Users, Calendar, PlayCircle, ArrowLeft, Mic } from 'lucide-react'

export default function UtaitePage() {
  const params = useParams()
  const router = useRouter()
  const utaite_name = decodeURIComponent(params?.utaite_name as string)
  
  const [songs, setSongs] = useState<SongEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [utaiteStats, setUtaiteStats] = useState<{
    totalSongs: number
    uniqueSongs: number
    uniqueArtists: string[]
    latestSong: SongEntry | null
    firstSong: SongEntry | null
  } | null>(null)

  useEffect(() => {
    if (utaite_name) {
      fetchUtaiteDetails()
    }
  }, [utaite_name])

  const fetchUtaiteDetails = async () => {
    console.log('🎤 우타이테 상세 정보 가져오기 시작:', utaite_name)
    
    try {
      // 우타이테가 부른 모든 노래 가져오기
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/utaites/songs?name=${encodeURIComponent(utaite_name)}`)
      
      if (!response.ok) {
        throw new Error('우타이테 정보를 찾을 수 없습니다.')
      }
      
      const data = await response.json()
      setSongs(data)
      console.log('✅ 우타이테 노래 정보:', data.length, '곡')

      // 통계 계산
      const uniqueArtists = Array.from(new Set(data.map((song: SongEntry) => song.song_artist)))
      const uniqueSongMasterIds = Array.from(new Set(data.map((song: SongEntry) => song.song_master_id)))
      
      // 최신/최오래된 노래 찾기
      const sortedSongs = data.sort((a: SongEntry, b: SongEntry) => 
        new Date(b.date).getTime() - new Date(a.date).getTime()
      )
      
      setUtaiteStats({
        totalSongs: data.length,
        uniqueSongs: uniqueSongMasterIds.length,
        uniqueArtists,
        latestSong: sortedSongs[0] || null,
        firstSong: sortedSongs[sortedSongs.length - 1] || null
      })
      
      console.log('✅ 우타이테 통계 계산 완료')
      
    } catch (error) {
      console.error('❌ 우타이테 정보 가져오기 실패:', error)
      alert(`우타이테 정보를 가져오는 중 오류가 발생했습니다: ${error.message}`)
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

  if (!utaiteStats) {
    return (
      <div className="min-h-screen bg-youtube-dark">
        <Header />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-white">우타이테를 찾을 수 없습니다.</div>
        </div>
      </div>
    )
  }

  // 아티스트별로 그룹화
  const songsByArtist = songs.reduce((acc, song) => {
    const artist = song.song_artist
    if (!acc[artist]) {
      acc[artist] = []
    }
    acc[artist].push(song)
    return acc
  }, {} as Record<string, SongEntry[]>)

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

        {/* 우타이테 정보 헤더 */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="bg-youtube-gray rounded-lg p-8">
            <div className="flex items-start gap-6">
              {/* 썸네일 */}
              {utaiteStats.latestSong && (
                <div className="flex-shrink-0">
                  <img 
                    src={utaiteStats.latestSong.thumbnail} 
                    alt={utaite_name}
                    className="w-48 h-32 object-cover rounded-lg"
                  />
                </div>
              )}
              
              {/* 우타이테 정보 */}
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-3 flex items-center">
                  <Mic className="w-8 h-8 mr-3 text-youtube-red" />
                  {utaite_name}
                </h1>
                
                <p className="text-xl text-gray-300 mb-4">우타이테</p>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  <div className="flex items-center gap-2 text-gray-400">
                    <PlayCircle className="w-5 h-5" />
                    <span>{utaiteStats.totalSongs}회 불렀음</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-400">
                    <Music className="w-5 h-5" />
                    <span>{utaiteStats.uniqueSongs}곡 (유니크)</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-400">
                    <Users className="w-5 h-5" />
                    <span>{utaiteStats.uniqueArtists.length}명의 아티스트</span>
                  </div>
                  
                  {utaiteStats.firstSong && (
                    <div className="flex items-center gap-2 text-gray-400">
                      <Calendar className="w-5 h-5" />
                      <span>첫 등록: {new Date(utaiteStats.firstSong.date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
                
                {/* 커버한 아티스트들 */}
                <div className="mt-4">
                  <p className="text-sm text-gray-400 mb-2">커버한 아티스트들:</p>
                  <div className="flex flex-wrap gap-2">
                    {utaiteStats.uniqueArtists.slice(0, 10).map(artist => {
                      const count = songs.filter(s => s.song_artist === artist).length
                      return (
                        <span 
                          key={artist}
                          className="px-3 py-1 bg-youtube-red text-white rounded-full text-sm cursor-pointer hover:bg-red-700 transition-colors"
                          onClick={() => router.push(`/artist/${encodeURIComponent(artist)}`)}
                        >
                          {artist} ({count}곡)
                        </span>
                      )
                    })}
                    {utaiteStats.uniqueArtists.length > 10 && (
                      <span className="px-3 py-1 bg-gray-600 text-white rounded-full text-sm">
                        +{utaiteStats.uniqueArtists.length - 10}명 더
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 아티스트별로 그룹화된 노래들 */}
        <div className="max-w-6xl mx-auto">
          <h3 className="text-2xl font-bold text-white mb-6">
            {utaite_name}이 부른 노래들 ({songs.length}곡)
          </h3>
          
          {Object.entries(songsByArtist)
            .sort(([,a], [,b]) => b.length - a.length) // 곡 수 많은 순으로 정렬
            .map(([artist, artistSongs]) => (
            <div key={artist} className="mb-8">
              {/* 아티스트 제목 */}
              <div className="flex items-center justify-between mb-4">
                <h4 
                  className="text-xl font-semibold text-white hover:text-youtube-red transition-colors cursor-pointer flex items-center gap-2"
                  onClick={() => router.push(`/artist/${encodeURIComponent(artist)}`)}
                >
                  <Users className="w-5 h-5" />
                  {artist}
                </h4>
                <span className="text-gray-400 text-sm">
                  {artistSongs.length}곡
                </span>
              </div>
              
              {/* 해당 아티스트의 노래들 */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {artistSongs
                  .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()) // 최신순 정렬
                  .map((song) => (
                  <SongCard key={song.id} song={song} />
                ))}
              </div>
            </div>
          ))}
          
          {songs.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>아직 이 우타이테가 부른 노래가 등록되지 않았습니다.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}