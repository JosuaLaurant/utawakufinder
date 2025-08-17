'use client'

import { Video } from '@/types'
import { User } from 'lucide-react'

interface SidebarProps {
  videos: Video[]
  selectedSinger: string
  onSingerSelect: (singer: string) => void
}

export default function Sidebar({ videos, selectedSinger, onSingerSelect }: SidebarProps) {
  // 우타이테별 곡 수 계산 및 정렬
  const singerCounts = videos.reduce((acc, video) => {
    if (video.singer) {
      acc[video.singer] = (acc[video.singer] || 0) + 1
    }
    return acc
  }, {} as Record<string, number>)

  const singers = Object.entries(singerCounts)
    .sort(([, a], [, b]) => b - a)  // 곡 수 내림차순 정렬
    .map(([singer]) => singer)

  return (
    <div className="fixed left-0 top-16 w-96 h-[calc(100vh-4rem)] bg-youtube-dark border-r border-gray-700 overflow-y-auto custom-scrollbar">
      <div className="p-4">
        <h2 className="text-white font-semibold mb-4 flex items-center">
          <User className="w-5 h-5 mr-2" />
          부른 사람 필터
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
            전체
          </button>
          
          {singers.map((singer) => (
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
                <span>{singer}</span>
                <span className="text-xs bg-gray-600 px-2 py-1 rounded-full">
                  {singerCounts[singer]}
                </span>
              </div>
            </button>
          ))}
        </div>

        {singers.length === 0 && (
          <p className="text-gray-500 text-sm mt-4">
            등록된 영상이 없습니다.
          </p>
        )}
      </div>
    </div>
  )
}