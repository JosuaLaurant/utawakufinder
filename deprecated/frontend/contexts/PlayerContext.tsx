'use client'

import React, { createContext, useContext, useState, useEffect, useRef } from 'react'

interface PlayerState {
  isPlaying: boolean
  currentSong: {
    id: string
    title: string
    artist: string
    utaite: string
    videoId: string
    startTime: number
  } | null
  volume: number
  duration: number
  currentTime: number
}

interface PlayerContextType {
  playerState: PlayerState
  isPlayerReady: boolean
  play: (song: {
    id: string
    title: string
    artist: string
    utaite: string
    videoId: string
    startTime: number
  }) => void
  pause: () => void
  stop: () => void
  setVolume: (volume: number) => void
  seekTo: (seconds: number) => void
}

const PlayerContext = createContext<PlayerContextType | undefined>(undefined)

declare global {
  interface Window {
    YT: any
    onYouTubeIframeAPIReady: () => void
  }
}

export function PlayerProvider({ children }: { children: React.ReactNode }) {
  const [playerState, setPlayerState] = useState<PlayerState>({
    isPlaying: false,
    currentSong: null,
    volume: 70,
    duration: 0,
    currentTime: 0
  })

  const playerRef = useRef<any>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const [isPlayerReady, setIsPlayerReady] = useState(false)

  // YouTube API 초기화
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // 외부 확장 프로그램 에러 필터링
      const originalConsoleError = console.error
      const originalConsoleWarn = console.warn
      
      // 전역 에러 이벤트 리스너로 확장 프로그램 에러 차단
      const handleError = (event: ErrorEvent) => {
        const message = event.message || ''
        const source = event.filename || ''
        
        if (message.includes('VDH') || 
            message.includes('getBasicInfo failed') ||
            message.includes('This video is unavailable') ||
            source.includes('youtube.js') ||
            source.includes('extension://')) {
          event.preventDefault()
          event.stopPropagation()
          return false
        }
      }
      
      window.addEventListener('error', handleError, true)
      
      console.error = (...args: any[]) => {
        const message = String(args[0] || '')
        const stack = (args[0]?.stack || '').toString()
        
        // VDH, youtube.js, 확장 프로그램 관련 에러 필터링
        if (message.includes('VDH') || 
            message.includes('getBasicInfo failed') ||
            message.includes('This video is unavailable') ||
            message.includes('youtube.js') ||
            stack.includes('youtube.js') ||
            stack.includes('extension://')) {
          return // 이런 에러는 무시
        }
        originalConsoleError.apply(console, args)
      }
      
      console.warn = (...args: any[]) => {
        const message = String(args[0] || '')
        if (message.includes('VDH') || 
            message.includes('youtube.js') ||
            message.includes('getBasicInfo') ||
            message.includes('This video is unavailable')) {
          return // 이런 경고는 무시
        }
        originalConsoleWarn.apply(console, args)
      }
      
      let retryCount = 0
      const maxRetries = 10
      
      const checkYTAPI = () => {
        console.log(`[${retryCount}] Checking YouTube API...`)
        
        if (window.YT && window.YT.Player) {
          console.log('✅ YouTube API already loaded')
          initializePlayer()
          return
        }
        
        // API 로드 완료 콜백 설정
        window.onYouTubeIframeAPIReady = () => {
          console.log('✅ YouTube API ready via callback')
          initializePlayer()
        }
        
        // 재시도 로직
        retryCount++
        if (retryCount < maxRetries) {
          console.log(`⏳ Waiting for YouTube API... (attempt ${retryCount}/${maxRetries})`)
          setTimeout(() => {
            if (!window.YT || !window.YT.Player) {
              checkYTAPI()
            }
          }, 1000 * retryCount) // 점진적으로 대기 시간 증가
        } else {
          console.error('❌ Failed to load YouTube API after maximum retries')
          // 수동으로 스크립트 로드 시도
          loadYouTubeAPIManually()
        }
      }
      
      const loadYouTubeAPIManually = () => {
        console.log('🔄 Manually loading YouTube API...')
        const existingScript = document.querySelector('script[src*="youtube.com/iframe_api"]')
        if (!existingScript) {
          const script = document.createElement('script')
          script.src = 'https://www.youtube.com/iframe_api'
          script.async = true
          script.onload = () => console.log('📜 YouTube API script loaded')
          script.onerror = () => console.error('❌ Failed to load YouTube API script')
          document.head.appendChild(script)
        }
      }
      
      // 초기 체크는 약간 지연 후 시작 (Next.js Script 로딩 대기)
      setTimeout(checkYTAPI, 500)
      
      // 클린업 함수
      return () => {
        window.removeEventListener('error', handleError, true)
        console.error = originalConsoleError
        console.warn = originalConsoleWarn
      }
    }
  }, [])

  const initializePlayer = () => {
    if (!window.YT || !window.YT.Player) {
      console.warn('YouTube API not loaded yet')
      setTimeout(initializePlayer, 100)
      return
    }

    // 숨겨진 플레이어 컨테이너 생성
    if (!document.getElementById('youtube-player')) {
      const playerDiv = document.createElement('div')
      playerDiv.id = 'youtube-player'
      playerDiv.style.display = 'none'
      document.body.appendChild(playerDiv)
    }

    try {
      playerRef.current = new window.YT.Player('youtube-player', {
        height: '360',
        width: '640',
        playerVars: {
          autoplay: 0,
          controls: 0,
          disablekb: 1,
          fs: 0,
          iv_load_policy: 3,
          modestbranding: 1,
          rel: 0,
          showinfo: 0
        },
        events: {
          onReady: (event: any) => {
            console.log('✅ YouTube Player onReady event')
            
            // 플레이어 메서드들이 실제로 사용 가능한지 확인 (playerRef.current는 이미 constructor에서 할당됨)
            const player = playerRef.current
            const requiredMethods = ['loadVideoById', 'playVideo', 'pauseVideo', 'setVolume']
            const availableMethods = requiredMethods.filter(method => typeof player?.[method] === 'function')
            
            console.log('Available methods on player:', availableMethods)
            console.log('PlayerRef current methods:', player ? Object.getOwnPropertyNames(player).filter(name => typeof player[name] === 'function').slice(0, 10) : 'no player')
            console.log('Event target methods:', event.target ? Object.getOwnPropertyNames(event.target).filter(name => typeof event.target[name] === 'function').slice(0, 10) : 'no target')
            
            if (availableMethods.length === requiredMethods.length) {
              console.log('✅ All YouTube Player methods available')
              setIsPlayerReady(true)
              
              // 초기 볼륨 설정
              if (player?.setVolume) {
                player.setVolume(70)
              }
            } else {
              console.warn('⚠️ Some YouTube Player methods not available:', {
                required: requiredMethods,
                available: availableMethods
              })
              // 조금 더 기다린 후 다시 체크
              setTimeout(() => {
                const laterMethods = requiredMethods.filter(method => typeof player?.[method] === 'function')
                if (laterMethods.length === requiredMethods.length) {
                  console.log('✅ YouTube Player methods available after delay')
                  setIsPlayerReady(true)
                }
              }, 1000)
            }
          },
          onStateChange: (event: any) => {
            const state = event.data
            if (state === window.YT.PlayerState.PLAYING) {
              setPlayerState((prev: PlayerState) => ({ ...prev, isPlaying: true }))
              startTimeTracking()
            } else if (state === window.YT.PlayerState.PAUSED || state === window.YT.PlayerState.ENDED) {
              setPlayerState((prev: PlayerState) => ({ ...prev, isPlaying: false }))
              stopTimeTracking()
            }
          },
          onError: (event: any) => {
            const errorCode = event.data
            let errorMessage = '재생 중 오류가 발생했습니다.'
            
            switch (errorCode) {
              case 2:
                errorMessage = '잘못된 비디오 ID입니다.'
                break
              case 5:
                errorMessage = '요청한 콘텐츠를 HTML5 플레이어에서 재생할 수 없습니다.'
                break
              case 100:
                errorMessage = '요청한 비디오를 찾을 수 없습니다. 비디오가 삭제되었거나 비공개로 설정되었을 수 있습니다.'
                break
              case 101:
              case 150:
                errorMessage = '비디오 소유자가 다른 웹사이트에서의 재생을 허용하지 않습니다.'
                break
              default:
                errorMessage = `알 수 없는 오류가 발생했습니다. (코드: ${errorCode})`
            }
            
            console.error('YouTube Player error:', { code: errorCode, message: errorMessage })
            
            setPlayerState((prev: PlayerState) => ({ 
              ...prev, 
              isPlaying: false,
              currentSong: null
            }))
            stopTimeTracking()
            
            // 사용자에게 알림
            alert(errorMessage)
          }
        }
      })
    } catch (error) {
      console.error('Failed to initialize YouTube player:', error)
      setTimeout(initializePlayer, 1000)
    }
  }

  const startTimeTracking = () => {
    if (intervalRef.current) clearInterval(intervalRef.current)
    
    intervalRef.current = setInterval(() => {
      if (playerRef.current && playerRef.current.getCurrentTime) {
        const currentTime = playerRef.current.getCurrentTime()
        const duration = playerRef.current.getDuration()
        
        setPlayerState((prev: PlayerState) => ({
          ...prev,
          currentTime,
          duration
        }))
      }
    }, 1000)
  }

  const stopTimeTracking = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const play = (song: {
    id: string
    title: string
    artist: string
    utaite: string
    videoId: string
    startTime: number
  }) => {
    console.log('🎵 Play attempt:', {
      isPlayerReady,
      hasPlayerRef: !!playerRef.current,
      hasLoadVideoById: typeof playerRef.current?.loadVideoById,
      playerRefMethods: playerRef.current ? Object.keys(playerRef.current).slice(0, 5) : 'no ref'
    })

    if (!isPlayerReady || !playerRef.current) {
      console.warn('YouTube player not ready yet. Player ready:', isPlayerReady, 'Player ref:', !!playerRef.current)
      alert('플레이어가 아직 준비되지 않았습니다. 잠시 후 다시 시도해주세요.')
      return
    }

    try {
      // 비디오 ID 유효성 검증
      if (!song.videoId || song.videoId.length !== 11) {
        console.error('Invalid video ID:', song.videoId)
        alert('잘못된 비디오 ID입니다.')
        return
      }

      // 새로운 곡이거나 다른 곡인 경우
      if (!playerState.currentSong || playerState.currentSong.id !== song.id) {
        console.log('🎵 새로운 곡 재생:', song.title)
        setPlayerState((prev: PlayerState) => ({
          ...prev,
          currentSong: song,
          isPlaying: false // 로딩 중이므로 false로 설정
        }))
        
        playerRef.current.loadVideoById({
          videoId: song.videoId,
          startSeconds: song.startTime
        })
      } else {
        // 같은 곡이면 재생/일시정지 토글
        console.log('🎵 같은 곡 토글:', playerState.isPlaying ? '일시정지' : '재생')
        if (playerState.isPlaying) {
          playerRef.current.pauseVideo()
        } else {
          playerRef.current.playVideo()
        }
      }
    } catch (error) {
      console.error('Error playing video:', error)
      alert('재생 중 오류가 발생했습니다.')
      setPlayerState((prev: PlayerState) => ({ 
        ...prev, 
        isPlaying: false,
        currentSong: null
      }))
    }
  }

  const pause = () => {
    if (playerRef.current && typeof playerRef.current.pauseVideo === 'function') {
      playerRef.current.pauseVideo()
    }
  }

  const stop = () => {
    if (playerRef.current && typeof playerRef.current.stopVideo === 'function') {
      playerRef.current.stopVideo()
      setPlayerState((prev: PlayerState) => ({
        ...prev,
        currentSong: null,
        isPlaying: false,
        currentTime: 0,
        duration: 0
      }))
      stopTimeTracking()
    }
  }

  const setVolume = (volume: number) => {
    if (playerRef.current && typeof playerRef.current.setVolume === 'function') {
      playerRef.current.setVolume(volume)
      setPlayerState((prev: PlayerState) => ({ ...prev, volume }))
    }
  }

  const seekTo = (seconds: number) => {
    if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
      playerRef.current.seekTo(seconds)
    }
  }

  return (
    <PlayerContext.Provider
      value={{
        playerState,
        isPlayerReady,
        play,
        pause,
        stop,
        setVolume,
        seekTo
      }}
    >
      {children}
    </PlayerContext.Provider>
  )
}

export function usePlayer() {
  const context = useContext(PlayerContext)
  if (context === undefined) {
    throw new Error('usePlayer must be used within a PlayerProvider')
  }
  return context
}