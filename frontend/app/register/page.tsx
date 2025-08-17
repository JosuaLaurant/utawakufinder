'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import TimestampModal from '@/components/TimestampModal'
import { Song } from '@/types'

export default function Register() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [parsedSongs, setParsedSongs] = useState<Song[]>([])
  const [videoInfo, setVideoInfo] = useState<any>(null)
  const [allParsedModes, setAllParsedModes] = useState<{[key: string]: Song[]}>({})
  const [activeParsingMode, setActiveParsingMode] = useState<string>('auto')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    console.log('🚀 URL 등록 시작:', url)
    setLoading(true)
    
    try {
      // 모든 파싱 모드 시도
      const modes = ['auto', 'setlist', 'simple', 'description', 'numbered']
      const allResults: {[key: string]: Song[]} = {}
      let videoInfoResult: any = null
      
      for (const mode of modes) {
        console.log(`📡 파싱 모드 ${mode} 시도 중...`)
        const requestUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/parse-video`
        
        const response = await fetch(requestUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url, parsing_mode: mode }),
        })

        if (!response.ok) {
          const errorText = await response.text()
          console.error(`❌ ${mode} 모드 실패:`, errorText)
          continue
        }

        const data = await response.json()
        allResults[mode] = data.songs || []
        videoInfoResult = data.video_info
        
        console.log(`🎵 ${mode} 모드 결과: ${allResults[mode].length}곡`)
      }
      
      // Unknown이 없는 모드 중에서 가장 많은 곡을 추출한 모드를 우선 선택
      let bestMode = 'auto'
      let maxSongs = 0
      let maxSongsWithUnknown = 0
      let bestModeWithUnknown = 'auto'
      
      for (const [mode, songs] of Object.entries(allResults)) {
        const unknownCount = songs.filter(song => 
          song.song_artist === 'Unknown' || song.song_artist === '' || !song.song_artist
        ).length
        
        console.log(`📊 ${mode} 모드: ${songs.length}곡 (Unknown: ${unknownCount}곡)`)
        
        if (unknownCount === 0 && songs.length > maxSongs) {
          // Unknown이 없는 모드 중 최대 곡 수
          maxSongs = songs.length
          bestMode = mode
          console.log(`✅ ${mode} 모드가 새로운 최적 모드로 선택됨 (Unknown 없음, ${songs.length}곡)`)
        }
        
        // Unknown이 있더라도 전체 최대 곡 수 기록 (fallback용)
        if (songs.length > maxSongsWithUnknown) {
          maxSongsWithUnknown = songs.length
          bestModeWithUnknown = mode
        }
      }
      
      // Unknown이 없는 모드가 하나도 없다면 전체 최대 곡 수 모드 선택
      if (maxSongs === 0) {
        bestMode = bestModeWithUnknown
        console.log(`⚠️ Unknown이 없는 모드가 없어서 fallback 모드 선택: ${bestMode} (${maxSongsWithUnknown}곡)`)
      }
      
      setAllParsedModes(allResults)
      setActiveParsingMode(bestMode)
      setParsedSongs(allResults[bestMode] || [])
      setVideoInfo(videoInfoResult)
      setShowModal(true)
      
      console.log(`🎯 최종 선택된 모드: ${bestMode} (${allResults[bestMode]?.length || 0}곡)`)
    } catch (error) {
      console.error('❌ URL 처리 실패:', error)
      alert(`URL 처리 중 오류가 발생했습니다: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async (confirmedSongs: Song[], singerName: string) => {
    console.log('💾 노래 저장 시작')
    console.log('📋 저장할 비디오 정보:', videoInfo)
    console.log('🎵 저장할 곡 수:', confirmedSongs.length)
    console.log('🎤 부른이:', singerName)
    
    try {
      const requestUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/save-songs`
      console.log('📡 저장 요청 URL:', requestUrl)
      
      const requestData = {
        video_info: videoInfo,
        video_url: url,
        songs: confirmedSongs,
        singer_override: singerName
      }
      console.log('📤 저장 요청 데이터:', requestData)
      
      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })

      console.log('📨 저장 응답 상태:', response.status, response.statusText)

      if (response.ok) {
        const result = await response.json()
        console.log('✅ 저장 성공:', result)
        alert('노래들이 성공적으로 등록되었습니다!')
        router.push('/')
      } else {
        const errorText = await response.text()
        console.error('❌ 저장 실패:', errorText)
        throw new Error(`저장 실패: HTTP ${response.status} - ${errorText}`)
      }
    } catch (error) {
      console.error('❌ 저장 중 에러:', error)
      console.error('상세 에러:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      })
      alert(`저장 중 오류가 발생했습니다: ${error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-youtube-dark">
      <Header />
      <div className="max-w-2xl mx-auto pt-20 px-6">
        <h1 className="text-3xl font-bold text-white mb-8 text-center">
          유튜브 노래방송 등록
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-2">
              유튜브 URL
            </label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full px-4 py-3 bg-youtube-gray border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-youtube-red focus:border-transparent"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-youtube-red hover:bg-red-700 disabled:bg-gray-600 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
          >
            {loading ? '처리 중...' : '등록하기'}
          </button>
        </form>

        <div className="mt-8 p-6 bg-youtube-gray rounded-lg">
          <h2 className="text-lg font-semibold text-white mb-4">사용 방법</h2>
          <ul className="text-gray-300 space-y-2">
            <li>• 유튜브 노래방송 URL을 입력하세요</li>
            <li>• 댓글에서 타임스탬프를 자동으로 추출합니다</li>
            <li>• 추출된 정보를 확인하고 수정할 수 있습니다</li>
            <li>• 댓글 형식: "시간 | 노래제목 | 가수"</li>
          </ul>
        </div>
      </div>

      {showModal && (
        <TimestampModal
          songs={parsedSongs}
          videoInfo={videoInfo}
          onConfirm={handleConfirm}
          onCancel={() => setShowModal(false)}
          allParsedModes={allParsedModes}
          activeParsingMode={activeParsingMode}
          onParsingModeChange={(mode, songs) => {
            setActiveParsingMode(mode)
            setParsedSongs(songs)
          }}
        />
      )}
    </div>
  )
}