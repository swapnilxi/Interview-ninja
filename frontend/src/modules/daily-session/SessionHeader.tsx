import React from 'react'

export default function SessionHeader({ title = 'Session' }: { title?: string }) {
  return (
    <header>
      <h2>{title}</h2>
    </header>
  )
}
