'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import SongCard from '@/components/SongCard'
import SongSidebar from '@/components/SongSidebar'
import { SongEntry } from '@/types'
import { Music } from 'lucide-react'

export default function Home() {
  const [songs, setSongs] = useState<SongEntry[]>([])
  const [filteredSongs, setFilteredSongs] = useState<SongEntry[]>([])
  const [selectedSinger, setSelectedSinger] = useState<string>('')
  const [selectedArtist, setSelectedArtist] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSongs()
  }, [])

  useEffect(() => {
    let filtered = songs
    
    // 부른이 필터링
    if (selectedSinger) {
      filtered = filtered.filter(song => song.utaite_name === selectedSinger)
    }
    
    // 원곡자 필터링
    if (selectedArtist) {
      filtered = filtered.filter(song => song.song_artist === selectedArtist)
    }
    
    setFilteredSongs(filtered)
  }, [selectedSinger, selectedArtist, songs])

  // 가수가 변경되면 아티스트 필터 초기화
  useEffect(() => {
    setSelectedArtist('')
  }, [selectedSinger])

  const fetchSongs = async () => {
    console.log('🎵 노래 목록 가져오기 시작')
    console.log('백엔드 URL:', process.env.NEXT_PUBLIC_BACKEND_URL)
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9030'
      const url = `${backendUrl}/songs`
      console.log('📡 요청 URL:', url)
      
      const response = await fetch(url)
      console.log('📨 응답 상태:', response.status, response.statusText)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('📋 받은 데이터:', data)
      console.log('🎵 노래 개수:', data.length)
      
      setSongs(data)
      setFilteredSongs(data)
      console.log('✅ 노래 목록 설정 완료')
    } catch (error) {
      console.error('❌ 노래 데이터 가져오기 실패:', error)
      console.error('상세 에러:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      })
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

  return (
    <div className="flex min-h-screen bg-youtube-dark">
      <SongSidebar 
        songs={songs}
        selectedSinger={selectedSinger}
        selectedArtist={selectedArtist}
        onSingerSelect={setSelectedSinger}
        onArtistSelect={setSelectedArtist}
      />
      <div className="flex-1 ml-72">
        <Header />
        <main className="pt-20 p-6 pb-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-white mb-4 flex items-center">
              <Music className="w-8 h-8 mr-3" />
              노래 목록
            </h1>
            
            <div className="flex items-center gap-4 text-gray-400">
              <p>{filteredSongs.length}곡의 노래가 있습니다.</p>
              {selectedSinger && (
                <span className="text-youtube-red">
                  • 부른이: {selectedSinger}
                </span>
              )}
              {selectedArtist && (
                <span className="text-youtube-red">
                  • 원곡자: {selectedArtist}
                </span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredSongs.map((song) => (
              <SongCard key={song.id} song={song} />
            ))}
          </div>

          {filteredSongs.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>등록된 노래가 없습니다.</p>
              <p>새로운 유튜브 URL을 등록해보세요!</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}