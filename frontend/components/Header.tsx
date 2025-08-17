'use client'

import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { Search, Plus, Music, User, Mic, Library } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')
  const router = useRouter()
  const pathname = usePathname()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <header className="fixed top-0 left-0 right-0 bg-youtube-dark border-b border-gray-700 z-50">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center space-x-6">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-youtube-red rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">U</span>
            </div>
            <span className="text-white font-bold text-xl">Utawakufinder</span>
          </Link>
          
          <nav className="flex items-center space-x-4">
            <Link
              href="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                pathname === '/' 
                  ? 'bg-youtube-red text-white' 
                  : 'text-gray-300 hover:text-white hover:bg-youtube-lightgray'
              }`}
            >
              <Music className="w-4 h-4" />
              <span>노래목록</span>
            </Link>
            <Link
              href="/songs"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                pathname === '/songs' 
                  ? 'bg-youtube-red text-white' 
                  : 'text-gray-300 hover:text-white hover:bg-youtube-lightgray'
              }`}
            >
              <Library className="w-4 h-4" />
              <span>악곡 정보</span>
            </Link>
            <Link
              href="/artists"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                pathname === '/artists' || pathname?.startsWith('/artist/') 
                  ? 'bg-youtube-red text-white' 
                  : 'text-gray-300 hover:text-white hover:bg-youtube-lightgray'
              }`}
            >
              <User className="w-4 h-4" />
              <span>아티스트</span>
            </Link>
            <Link
              href="/utaites"
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                pathname === '/utaites' || pathname?.startsWith('/utaite/') 
                  ? 'bg-youtube-red text-white' 
                  : 'text-gray-300 hover:text-white hover:bg-youtube-lightgray'
              }`}
            >
              <Mic className="w-4 h-4" />
              <span>우타이테</span>
            </Link>
          </nav>
        </div>

        <form onSubmit={handleSearch} className="flex-1 max-w-2xl mx-8">
          <div className="flex">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="노래 제목, 아티스트, 우타이테로 검색..."
              className="flex-1 px-4 py-2 bg-youtube-gray border border-gray-600 rounded-l-full text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-youtube-lightgray border border-gray-600 border-l-0 rounded-r-full hover:bg-gray-600 transition-colors"
            >
              <Search className="w-5 h-5 text-gray-300" />
            </button>
          </div>
        </form>

        <Link
          href="/register"
          className="flex items-center space-x-2 bg-youtube-red hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>등록</span>
        </Link>
      </div>
    </header>
  )
}