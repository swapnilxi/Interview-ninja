import React from 'react'
import ApiKeyManager from './components/ApiKeyManager'
import ConfigInteractive from './components/ConfigInteractive'
import ModelSelector from './components/ModelSelector'

export default function ConfigPage() {
  return (
    <main>
      <h2>Config</h2>
      <ApiKeyManager />
      <ConfigInteractive />
      <ModelSelector />
    </main>
  )
}
