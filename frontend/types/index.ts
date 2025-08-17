export interface Song {
  start_time: string
  song_name: string
  song_artist: string
}

export interface SongEntry {
  id: string
  song_master_id?: string  // 새로운 필드 추가
  song_name: string
  song_artist: string
  start_time: string
  video_id: string
  video_title: string
  video_url: string
  channel: string
  singer: string
  date: string
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