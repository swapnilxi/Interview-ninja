import React from 'react'

export default function QuestionCard({ question }: { question?: any }) {
  return (
    <article>
      <h3>{question?.title || 'Question Title'}</h3>
      <p>{question?.body || 'Question body or prompt goes here.'}</p>
    </article>
  )
}
