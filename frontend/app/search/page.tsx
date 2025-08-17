'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import Header from '@/components/Header'
import SongCard from '@/components/SongCard'
import { SongEntry } from '@/types'
import { Music } from 'lucide-react'

export default function Search() {
  const searchParams = useSearchParams()
  const query = searchParams?.get('q') || ''
  const [songs, setSongs] = useState<SongEntry[]>([])
  const [filteredSongs, setFilteredSongs] = useState<SongEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSongs()
  }, [])

  useEffect(() => {
    if (query && songs.length > 0) {
      const filtered = songs.filter(song => {
        const searchText = query.toLowerCase()
        return (
          song.song_title.toLowerCase().includes(searchText) ||
          song.song_artist.toLowerCase().includes(searchText) ||
          song.utaite_name.toLowerCase().includes(searchText) ||
          song.video_title.toLowerCase().includes(searchText) ||
          song.video_channel.toLowerCase().includes(searchText)
        )
      })
      setFilteredSongs(filtered)
    } else if (!query) {
      setFilteredSongs(songs)
    }
    setLoading(false)
  }, [query, songs])

  const fetchSongs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/songs`)
      const data = await response.json()
      setSongs(data)
    } catch (error) {
      console.error('노래 데이터 가져오기 실패:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-youtube-dark">
        <Header />
        <div className="pt-20 flex items-center justify-center">
          <div className="text-white">검색 중...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-youtube-dark">
      <Header />
      <div className="pt-20 px-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white mb-2 flex items-center">
            <Music className="w-8 h-8 mr-3" />
            "{query}" 검색 결과
          </h1>
          <p className="text-gray-400">
            {filteredSongs.length}곡의 노래를 찾았습니다.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredSongs.map((song) => (
            <SongCard key={song.id} song={song} />
          ))}
        </div>

        {query && filteredSongs.length === 0 && songs.length > 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p>"{query}"에 대한 검색 결과가 없습니다.</p>
            <p>다른 검색어로 시도해보세요.</p>
          </div>
        )}

        {!query && (
          <div className="text-center text-gray-400 mt-20">
            <p>검색어를 입력해주세요.</p>
          </div>
        )}
      </div>
    </div>
  )
}