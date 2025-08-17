export interface Song {
  start_time: string
  song_name: string
  song_artist: string
}

export interface SongEntry {
  id: number
  start_time: string
  date: string
  song_id: number
  song_title: string  // API response field
  song_artist: string  // API response field
  utaite_id: number
  utaite_name: string  // API response field
  video_id: string
  video_title: string  // API response field
  video_channel: string  // API response field
  thumbnail_url: string  // API response field
  
  // 기존 호환성을 위한 필드들 (computed)
  song_name?: string
  singer?: string
  video_url?: string
  channel?: string
  thumbnail?: string
}

export interface Video {
  id: string
  title: string
  channel: string
  singer: string
  date: string
  thumbnail?: string
  songs: Song[]
}

export interface VideoInfo {
  id: string
  title: string
  channel: string
  thumbnail?: string
}