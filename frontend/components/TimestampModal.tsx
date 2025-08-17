'use client'

import { useState } from 'react'
import { Song, VideoInfo } from '@/types'
import { X, Edit2, Check } from 'lucide-react'

interface TimestampModalProps {
  songs: Song[]
  videoInfo: VideoInfo
  onConfirm: (songs: Song[], singerName: string) => void
  onCancel: () => void
  allParsedModes?: {[key: string]: Song[]}
  activeParsingMode?: string
  onParsingModeChange?: (mode: string, songs: Song[]) => void
}

export default function TimestampModal({ 
  songs, 
  videoInfo, 
  onConfirm, 
  onCancel, 
  allParsedModes, 
  activeParsingMode, 
  onParsingModeChange 
}: TimestampModalProps) {
  const [editedSongs, setEditedSongs] = useState<Song[]>(songs)
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [currentMode, setCurrentMode] = useState<string>(activeParsingMode || 'auto')
  const [editingSinger, setEditingSinger] = useState(false)
  const [singerName, setSingerName] = useState<string>(() => {
    // 초기 singer 이름 추출
    const channel = videoInfo.channel
    return channel.split('/')[0].trim() || channel.split('・')[0].trim() || channel.split(' ')[0].trim()
  })

  const handleEdit = (index: number, field: keyof Song, value: string) => {
    const updated = [...editedSongs]
    updated[index] = { ...updated[index], [field]: value }
    setEditedSongs(updated)
  }

  const handleRemove = (index: number) => {
    const updated = editedSongs.filter((_, i) => i !== index)
    setEditedSongs(updated)
  }

  const handleConfirm = () => {
    onConfirm(editedSongs, singerName)
  }

  const handleModeChange = (mode: string) => {
    if (allParsedModes && allParsedModes[mode]) {
      setCurrentMode(mode)
      setEditedSongs(allParsedModes[mode])
      onParsingModeChange?.(mode, allParsedModes[mode])
    }
  }

  const modeLabels = {
    auto: '1번',
    setlist: '2번',
    simple: '3번',
    description: '4번',
    numbered: '5번'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-youtube-gray rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-600">
          <div>
            <h2 className="text-xl font-bold text-white">타임스탬프 확인</h2>
            <p className="text-gray-300 text-sm mt-1">{videoInfo.title}</p>
            <p className="text-gray-400 text-xs mt-1">채널: {videoInfo.channel}</p>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {/* 파싱 모드 탭 */}
          {allParsedModes && Object.keys(allParsedModes).length > 1 && (
            <div className="mb-6 border-b border-gray-600">
              <nav className="flex space-x-8">
                {Object.entries(allParsedModes).map(([mode, modeSongs]) => (
                  <button
                    key={mode}
                    onClick={() => handleModeChange(mode)}
                    className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      currentMode === mode
                        ? 'border-youtube-red text-white'
                        : 'border-transparent text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    {modeLabels[mode as keyof typeof modeLabels] || mode} ({modeSongs.length}곡)
                  </button>
                ))}
              </nav>
            </div>
          )}

          {/* Singer 편집 섹션 */}
          <div className="mb-6 bg-youtube-lightgray rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-white font-semibold">부른이 정보</h3>
              {!editingSinger && (
                <button
                  onClick={() => setEditingSinger(true)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
              )}
            </div>
            
            {editingSinger ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={singerName}
                  onChange={(e) => setSingerName(e.target.value)}
                  className="flex-1 px-3 py-2 bg-youtube-dark border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-youtube-red"
                  placeholder="부른이 이름을 입력하세요"
                />
                <button
                  onClick={() => setEditingSinger(false)}
                  className="px-3 py-2 bg-youtube-red hover:bg-red-700 text-white rounded text-sm transition-colors flex items-center gap-1"
                >
                  <Check className="w-4 h-4" />
                  확인
                </button>
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <span className="text-youtube-red font-semibold">{singerName}</span>
                <span className="text-gray-400 text-xs">← 저장시 이 이름으로 등록됩니다</span>
              </div>
            )}
          </div>

          <div className="mb-4">
            <p className="text-gray-300 text-sm">
              추출된 정보를 확인하고 필요시 수정해주세요. 형식: "시간 | 노래제목 | 가수"
            </p>
          </div>

          <div className="space-y-2">
            {editedSongs.map((song, index) => (
              <div key={index} className="bg-youtube-dark p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">#{index + 1}</span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setEditingIndex(editingIndex === index ? null : index)}
                      className="text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      {editingIndex === index ? <Check className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => handleRemove(index)}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {editingIndex === index ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">시간</label>
                      <input
                        type="text"
                        value={song.start_time}
                        onChange={(e) => handleEdit(index, 'start_time', e.target.value)}
                        className="w-full px-3 py-2 bg-youtube-gray border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500"
                        placeholder="0:00:00"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">노래제목</label>
                      <input
                        type="text"
                        value={song.song_name}
                        onChange={(e) => handleEdit(index, 'song_name', e.target.value)}
                        className="w-full px-3 py-2 bg-youtube-gray border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500"
                        placeholder="노래 제목"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">가수</label>
                      <input
                        type="text"
                        value={song.song_artist}
                        onChange={(e) => handleEdit(index, 'song_artist', e.target.value)}
                        className="w-full px-3 py-2 bg-youtube-gray border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-blue-500"
                        placeholder="가수명"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="text-white">
                    <span className="font-mono text-blue-400">{song.start_time}</span>
                    <span className="mx-2 text-gray-400">|</span>
                    <span className="font-medium">{song.song_name}</span>
                    <span className="mx-2 text-gray-400">|</span>
                    <span className="text-gray-300">{song.song_artist}</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {editedSongs.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              추출된 타임스탬프가 없습니다.
            </div>
          )}
        </div>

        <div className="flex items-center justify-between p-6 border-t border-gray-600">
          <div className="text-gray-300 text-sm">
            총 {editedSongs.length}곡이 추출되었습니다.
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-gray-300 border border-gray-600 rounded-lg hover:bg-youtube-lightgray transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleConfirm}
              className="px-4 py-2 bg-youtube-red hover:bg-red-700 text-white rounded-lg transition-colors"
              disabled={editedSongs.length === 0}
            >
              확인
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}