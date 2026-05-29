import React from 'react'
import SessionHeader from './components/SessionHeader'
import QuestionCard from './components/QuestionCard'
import NavigationControl from './components/NavigationControl'
import SessionSummary from './components/SessionSummary'

export default function DailySessionPage() {
  return (
    <main>
      <SessionHeader title="Daily Session" />
      <QuestionCard />
      <NavigationControl />
      <SessionSummary />
    </main>
  )
}
