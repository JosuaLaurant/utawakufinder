import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '우타와쿠 파인더',
  description: '유튜브 노래방송 타임스탬프 검색 서비스',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>
        <div>
          {children}
        </div>
      </body>
    </html>
  )
}