'use client'

import { SongEntry } from '@/types'
import { User, Music, Mic } from 'lucide-react'

interface SongSidebarProps {
  songs: SongEntry[]
  selectedSinger: string
  selectedArtist?: string
  onSingerSelect: (singer: string) => void
  onArtistSelect?: (artist: string) => void
}

export default function SongSidebar({ 
  songs, 
  selectedSinger, 
  selectedArtist, 
  onSingerSelect, 
  onArtistSelect 
}: SongSidebarProps) {
  // 우타이테 목록을 곡 수별로 정렬
  const singerCounts = songs.reduce((acc, song) => {
    if (song.utaite_name) {
      acc[song.utaite_name] = (acc[song.utaite_name] || 0) + 1
    }
    return acc
  }, {} as Record<string, number>)
  
  const singers = Object.keys(singerCounts).sort((a, b) => singerCounts[b] - singerCounts[a])
  
  // 아티스트 목록을 곡 수별로 정렬
  const artistCounts = songs.reduce((acc, song) => {
    if (song.song_artist) {
      acc[song.song_artist] = (acc[song.song_artist] || 0) + 1
    }
    return acc
  }, {} as Record<string, number>)
  
  const artists = Object.keys(artistCounts).sort((a, b) => artistCounts[b] - artistCounts[a])

  const getFilteredSongCount = (singer?: string, artist?: string) => {
    return songs.filter(song => {
      const singerMatch = singer ? song.utaite_name === singer : true
      const artistMatch = artist ? song.song_artist === artist : true
      return singerMatch && artistMatch
    }).length
  }

  return (
    <div className="fixed left-0 top-16 w-72 h-[calc(100vh-4rem)] bg-youtube-dark border-r border-gray-700 overflow-y-auto custom-scrollbar">
      <div className="p-4">
        {/* 부른 사람 필터 */}
        <div className="mb-6">
          <h2 className="text-white font-semibold mb-4 flex items-center">
            <User className="w-5 h-5 mr-2" />
            부른 사람
          </h2>
          
          <div className="space-y-2">
            <button
              onClick={() => onSingerSelect('')}
              className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                selectedSinger === '' 
                  ? 'bg-youtube-red text-white' 
                  : 'text-gray-300 hover:bg-youtube-gray hover:text-white'
              }`}
            >
              <div className="flex justify-between items-center">
                <span>전체</span>
                <span className="text-xs bg-gray-600 px-2 py-1 rounded">
                  {getFilteredSongCount()}
                </span>
              </div>
            </button>
            
            {singers.map((singer) => {
              const count = getFilteredSongCount(singer)
              return (
                <button
                  key={singer}
                  onClick={() => onSingerSelect(singer)}
                  className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                    selectedSinger === singer 
                      ? 'bg-youtube-red text-white' 
                      : 'text-gray-300 hover:bg-youtube-gray hover:text-white'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="truncate">{singer}</span>
                    <span className="text-xs bg-gray-600 px-2 py-1 rounded">
                      {count}
                    </span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* 아티스트 필터 (선택사항) */}
        {onArtistSelect && (
          <div className="mb-6">
            <h2 className="text-white font-semibold mb-4 flex items-center">
              <Mic className="w-5 h-5 mr-2" />
              아티스트
            </h2>
            
            <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
              <button
                onClick={() => onArtistSelect('')}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  selectedArtist === '' 
                    ? 'bg-youtube-red text-white' 
                    : 'text-gray-300 hover:bg-youtube-gray hover:text-white'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span>전체</span>
                  <span className="text-xs bg-gray-600 px-2 py-1 rounded">
                    {getFilteredSongCount(selectedSinger)}
                  </span>
                </div>
              </button>
              
              {artists.map((artist) => {
                const count = getFilteredSongCount(selectedSinger, artist)
                return (
                  <button
                    key={artist}
                    onClick={() => onArtistSelect(artist)}
                    className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                      selectedArtist === artist 
                        ? 'bg-youtube-red text-white' 
                        : 'text-gray-300 hover:bg-youtube-gray hover:text-white'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="truncate text-sm">{artist}</span>
                      <span className="text-xs bg-gray-600 px-2 py-1 rounded">
                        {count}
                      </span>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {songs.length === 0 && (
          <p className="text-gray-500 text-sm mt-4">
            등록된 노래가 없습니다.
          </p>
        )}
      </div>
    </div>
  )
}