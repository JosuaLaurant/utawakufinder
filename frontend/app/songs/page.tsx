'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/Header'
import { Music, User, TrendingUp, Calendar } from 'lucide-react'

interface SongMaster {
  id: string
  titles: {
    original: string
    korean?: string
    english?: string
    romanized?: string
  }
  artist: {
    original: string
    korean?: string
    english?: string
    romanized?: string
  }
  tags: string[]
  performance_count: number
}

interface Performance {
  id: string
  start_time: string
  video_id: string
  video_title: string
  singer: string
  date: string
  thumbnail: string
}

interface SongWithPerformances {
  song: SongMaster
  performances: Performance[]
  latest_performance?: Performance
}

export default function SongsPage() {
  const [songs, setSongs] = useState<SongWithPerformances[]>([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState<'performance_count' | 'latest' | 'alphabetical'>('performance_count')

  useEffect(() => {
    fetchSongs()
  }, [])

  const fetchSongs = async () => {
    try {
      setLoading(true)
      
      // 곡 마스터와 부른 기록을 동시에 가져오기
      const [songsResponse, performancesResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/songs/master`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/songs`)
      ])
      
      if (!songsResponse.ok || !performancesResponse.ok) {
        throw new Error('데이터를 가져오는데 실패했습니다')
      }
      
      const songsData: SongMaster[] = await songsResponse.json()
      const performancesData: Performance[] = await performancesResponse.json()
      
      // 곡별로 부른 기록 그룹화
      const songWithPerformances: SongWithPerformances[] = songsData.map(song => {
        const songPerformances = performancesData.filter(p => p.song_master_id === song.id)
        const latestPerformance = songPerformances.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())[0]
        
        return {
          song,
          performances: songPerformances,
          latest_performance: latestPerformance
        }
      })
      
      setSongs(songWithPerformances)
    } catch (error) {
      console.error('악곡 정보 가져오기 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const sortedSongs = [...songs].sort((a, b) => {
    switch (sortBy) {
      case 'performance_count':
        return b.song.performance_count - a.song.performance_count
      case 'latest':
        const aDate = a.latest_performance ? new Date(a.latest_performance.date) : new Date(0)
        const bDate = b.latest_performance ? new Date(b.latest_performance.date) : new Date(0)
        return bDate.getTime() - aDate.getTime()
      case 'alphabetical':
        return a.song.titles.original.localeCompare(b.song.titles.original)
      default:
        return 0
    }
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-youtube-dark">
        <Header />
        <div className="pt-16 flex items-center justify-center h-96">
          <div className="text-white text-lg">악곡 정보를 불러오는 중...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-youtube-dark">
      <Header />
      <main className="pt-16 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Music className="w-8 h-8 text-youtube-red" />
              <h1 className="text-3xl font-bold text-white">악곡 정보</h1>
              <span className="text-gray-400 text-lg">({songs.length}곡)</span>
            </div>
            
            <div className="flex items-center space-x-2">
              <span className="text-gray-400 text-sm">정렬:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="bg-youtube-gray border border-gray-600 text-white px-3 py-1 rounded-lg text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="performance_count">부른 횟수</option>
                <option value="latest">최근 부른 날짜</option>
                <option value="alphabetical">가나다순</option>
              </select>
            </div>
          </div>

          <div className="grid gap-4">
            {sortedSongs.map((item) => (
              <div
                key={item.song.id}
                className="bg-youtube-gray border border-gray-700 rounded-lg p-6 hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-semibold text-white truncate">
                        {item.song.titles.original}
                      </h3>
                      {item.song.titles.korean && (
                        <span className="text-gray-400 text-sm">
                          ({item.song.titles.korean})
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-gray-300 mb-3">
                      <div className="flex items-center space-x-1">
                        <User className="w-4 h-4" />
                        <span>{item.song.artist.original}</span>
                        {item.song.artist.korean && (
                          <span className="text-gray-500 text-sm">
                            ({item.song.artist.korean})
                          </span>
                        )}
                      </div>
                    </div>

                    {item.song.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {item.song.tags.map((tag) => (
                          <span
                            key={tag}
                            className="bg-gray-600 text-gray-300 px-2 py-1 rounded-full text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="flex items-center space-x-6 text-sm text-gray-400">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="w-4 h-4" />
                        <span>부른 횟수: {item.song.performance_count}회</span>
                      </div>
                      {item.latest_performance && (
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>최근: {formatDate(item.latest_performance.date)}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {item.latest_performance && (
                    <div className="flex-shrink-0 ml-4">
                      <img
                        src={item.latest_performance.thumbnail}
                        alt={item.latest_performance.video_title}
                        className="w-24 h-16 object-cover rounded-lg"
                      />
                      <div className="text-xs text-gray-400 mt-1 text-center truncate w-24">
                        {item.latest_performance.singer}
                      </div>
                    </div>
                  )}
                </div>

                {item.performances.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-600">
                    <details className="text-sm">
                      <summary className="text-gray-400 cursor-pointer hover:text-white transition-colors">
                        부른 기록 {item.performances.length}개 보기
                      </summary>
                      <div className="mt-3 space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                        {item.performances
                          .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                          .map((performance) => (
                            <div
                              key={performance.id}
                              className="flex items-center justify-between py-2 px-3 bg-gray-600 rounded-lg"
                            >
                              <div className="flex items-center space-x-3">
                                <img
                                  src={performance.thumbnail}
                                  alt={performance.video_title}
                                  className="w-12 h-8 object-cover rounded"
                                />
                                <div>
                                  <div className="text-white font-medium">{performance.singer}</div>
                                  <div className="text-gray-400 text-xs truncate max-w-xs">
                                    {performance.video_title}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="text-white text-sm">{performance.start_time}</div>
                                <div className="text-gray-400 text-xs">{formatDate(performance.date)}</div>
                              </div>
                            </div>
                          ))}
                      </div>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}