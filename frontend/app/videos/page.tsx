'use client'

import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import VideoCard from '@/components/VideoCard'
import Header from '@/components/Header'
import { Video } from '@/types'

export default function Videos() {
  const [videos, setVideos] = useState<Video[]>([])
  const [filteredVideos, setFilteredVideos] = useState<Video[]>([])
  const [selectedSinger, setSelectedSinger] = useState<string>('')

  useEffect(() => {
    fetchVideos()
  }, [])

  useEffect(() => {
    if (selectedSinger) {
      setFilteredVideos(videos.filter(video => video.singer === selectedSinger))
    } else {
      setFilteredVideos(videos)
    }
  }, [selectedSinger, videos])

  const fetchVideos = async () => {
    console.log('🎬 비디오 목록 가져오기 시작')
    console.log('백엔드 URL:', process.env.NEXT_PUBLIC_BACKEND_URL)
    
    try {
      const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/videos`
      console.log('📡 요청 URL:', url)
      
      const response = await fetch(url)
      console.log('📨 응답 상태:', response.status, response.statusText)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      console.log('📋 받은 데이터:', data)
      console.log('📊 비디오 개수:', data.length)
      
      setVideos(data)
      setFilteredVideos(data)
      console.log('✅ 비디오 목록 설정 완료')
    } catch (error) {
      console.error('❌ 비디오 데이터 가져오기 실패:', error)
      console.error('상세 에러:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      })
    }
  }

  return (
    <div className="flex min-h-screen bg-youtube-dark">
      <Sidebar 
        videos={videos}
        selectedSinger={selectedSinger}
        onSingerSelect={setSelectedSinger}
      />
      <div className="flex-1 ml-96">
        <Header />
        <main className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredVideos.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
          {filteredVideos.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p>등록된 영상이 없습니다.</p>
              <p>새로운 유튜브 URL을 등록해보세요!</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}